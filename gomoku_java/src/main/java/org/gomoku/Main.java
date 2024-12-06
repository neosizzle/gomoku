package org.gomoku;

import io.grpc.Server;
import io.grpc.ServerBuilder;

import java.io.IOException;


public class Main {
    public static void main(String[] args) throws InterruptedException, IOException {
        int port = 50053;
        Server server = ServerBuilder.forPort(port)
                .addService(new GameService(11))
                .build();

        server.start();
        System.out.println("Server started on port " + port + "...");

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.err.println("Shutting down server...");
            try {
                server.shutdown().awaitTermination();
                System.out.println("Server shut down successfully.");
            } catch (InterruptedException e) {
                System.err.println("Error during server shutdown: " + e.getMessage());
                Thread.currentThread().interrupt();
            }
        }));

        server.awaitTermination();
    }
}
