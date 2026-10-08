package com.instaunlike;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

public class JobService {
    private static void respond(HttpExchange exchange, int status, String body)
            throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(status, bytes.length);
        try (var output = exchange.getResponseBody()) {
            output.write(bytes);
        }
    }

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 8080), 0);

        server.createContext("/api/health", exchange -> {
            if (!"GET".equals(exchange.getRequestMethod())) {
                respond(exchange, 405, "{\"success\":false,\"error\":\"Method not allowed\"}");
                return;
            }
            respond(exchange, 200,
                "{\"success\":true,\"service\":\"java-job-service\",\"message\":\"Java service is running\"}");
        });

        server.createContext("/api/info", exchange ->
            respond(exchange, 200,
                "{\"service\":\"java-job-service\",\"role\":\"workflow orchestration foundation\",\"databaseOwner\":\"python-api\"}")
        );

        server.start();
        System.out.println("Java service running at http://127.0.0.1:8080");
    }
}
