#! /usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import print_function
import grpc
from example import helloworld_pb2, helloworld_pb2_grpc


# 仅供测试用的客户端代码
def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
    print("Greeter client received: " + response.message)


if __name__ == '__main__':
    run()
