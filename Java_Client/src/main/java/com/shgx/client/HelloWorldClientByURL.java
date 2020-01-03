package com.shgx.client;

import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

/**
 * @author: guangxush
 * @create: 2020/01/03
 */
public class HelloWorldClientByURL {

    public static void main(String[] args) {
        RestTemplate restTemplate = new RestTemplate();
        String url = "http://127.0.0.1:5000/hello/world";
        ResponseEntity<String> responseEntity = restTemplate.getForEntity(url, String.class);
        String result = responseEntity.getBody();
        System.out.println(result);
    }
}
