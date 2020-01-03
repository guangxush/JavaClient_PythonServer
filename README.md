### Java客户端调用Python服务端

#### 使用Web Service调用

0. 安装依赖
Python: pip install flask

Java在maven中加入相关的包
```xml
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-web</artifactId>
    <version>5.2.2.RELEASE</version>
</dependency>
```

1. Python服务端采用Flash便携式路由，并调用深度学习服务（这里简单用Hello World代替）
```python
from flask import Flask
app = Flask(__name__)
# 使用<param>传递参数
@app.route('/hello/<param>')
def hello_get(param):
    return 'hello %s' % param

if __name__ == '__main__':
    app.run()
```

2. Java客户端采用RestTemplate请求URL并返回结果
```java
public class HelloWorldClientByURL {
    public static void main(String[] args) {
        RestTemplate restTemplate = new RestTemplate();
        String url = "http://127.0.0.1:5000/hello/world";
        ResponseEntity<String> responseEntity = restTemplate.getForEntity(url, String.class);
        String result = responseEntity.getBody();
        System.out.println(result);
    }
}
```
3. 先开启Python服务端，然后执行Java客户端，这时返回结果
```text
hello world
```


#### 使用gRPC，服务端直接将Python服务注册到gRPC, Java客户端根据端口号通过gRPC注册中心调用服务端服务

0. 安装依赖
Python: pipinstall grpcio / pipinstall grpcio-tls

Java在maven中加入相关的依赖：
```xml
<dependency>
    <groupId>io.grpc</groupId>
    <artifactId>grpc-netty-shaded</artifactId>
    <version>1.15.0</version>
</dependency>
<dependency>
    <groupId>io.grpc</groupId>
    <artifactId>grpc-protobuf</artifactId>
    <version>1.15.0</version>
</dependency>
<dependency>
    <groupId>io.grpc</groupId>
    <artifactId>grpc-stub</artifactId>
    <version>1.15.0</version>
</dependency>
```

1. Python服务端代码

```python
# python服务端代码
class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
```

2. 编写helloworld.proto,并执行

```proto
syntax = "proto3";
package example;

// The greeting service definition.
service Greeter {
  // Sends a greeting
  rpc SayHello (HelloRequest) returns (HelloReply) {}
}

// The request message containing the user's name.
message HelloRequest {
  string name = 1;
}

// The response message containing the greetings
message HelloReply {
  string message = 1;
}
```

在相关目录下执行```python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./helloworld.proto ```进行编译

3. Java客户端代码

```java
public class HelloWorldClient {

    private static final Logger logger = Logger.getLogger(HelloWorldClient.class.getName());

    private final ManagedChannel channel;
    private final GreeterGrpc.GreeterBlockingStub blockingStub;

    /**
     * Construct client connecting to HelloWorld server at {@code host:port}.
     */
    public HelloWorldClient(String host, int port) {

        channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext(true)
                .build();
        blockingStub = GreeterGrpc.newBlockingStub(channel);
    }

    public void shutdown() throws InterruptedException {
        channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
    }

    /**
     * Say hello to server.
     */
    public void greet(String name) {
        logger.info("Will try to greet " + name + " ...");
        HelloRequest request = HelloRequest.newBuilder().setName(name).build();
        HelloReply response;
        try {
            response = blockingStub.sayHello(request);
        } catch (StatusRuntimeException e) {
            logger.log(Level.WARNING, "RPC failed: {0}", e.getStatus());
            return;
        }
        logger.info("Greeting: " + response.getMessage());
    }

    /**
     * Greet server. If provided, the first element of {@code args} is the name to use in the
     * greeting.
     */
    public static void main(String[] args) throws Exception {
        HelloWorldClient client = new HelloWorldClient("localhost", 50051);
        try {

            String user = "world";
            if (args.length > 0) {
                user = args[0];
            }
            client.greet(user);
        } finally {
            client.shutdown();
        }
    }
}
```

4. 编写helloworld.proto参数与2保持一致

```proto
syntax = "proto3";
package example;
option java_package = "com.shgx.grpc";
option java_outer_classname = "HelloWorldServiceProto";
option java_multiple_files = true;

// The greeting service definition.
service Greeter {
    // Sends a greeting
    rpc SayHello (HelloRequest) returns (HelloReply) {}
}

// The request message containing the user's name.
message HelloRequest {
    string name = 1;
}

// The response message containing the greetings
message HelloReply {
    string message = 1;
}
```

5. 先启动Python服务端代码，然后启动Java客户端，输出结果

```text
hello world
```
#### 两种方式对比

1. 采用Web服务进行调用，后端对应用的处理线程采用同步阻塞的模型，阻塞的时间取决对方I/O处理的速度和网络I/O传输的速度，两种不同代码之间通过HTTP请求或者JSON封装进行交互，效率较低

2. 采用gRPC，有了服务的注册中心，服务切换更新更加轻量化，并且遵循 Netty 的线程分工原则，协议层消息的接收和编解码由Netty 的 I/O(NioEventLoop)线程负责；后续应用层的处理由应用线程负责，防止由于应用处理耗时而阻塞 Netty 的 I/O 线程， 可以通过服务名和方法名调用，直接调用启动的时候注册的服务实例，不需要反射或者JSON编码解码进行调用，性能更优


#### 参考文档

[gRPC 官方文档中文版](https://doc.oschina.net/grpc?t=58009)


