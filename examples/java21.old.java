package com.example.legacy;

import java.util.*;
import java.util.concurrent.*;

/**
 * EJEMPLO: Código Legacy que se beneficiaría de Java 21
 * Este código funciona, pero podría ser mucho mejor con Java 21
 */
public class LegacyCodeExample {
    
    // ❌ ThreadLocal en lugar de ScopedValue
    private static final ThreadLocal<User> currentUser = new ThreadLocal<>();
    
    // ❌ Platform thread pool en lugar de Virtual Threads
    private final ExecutorService executor = Executors.newFixedThreadPool(100);
    
    /**
     * ❌ Problema: Platform threads limitan concurrencia
     * ✅ Java 21: Executors.newVirtualThreadPerTaskExecutor()
     */
    public List<UserData> fetchUserDataParallel(List<Long> userIds) 
            throws Exception {
        
        List<Future<UserData>> futures = new ArrayList<>();
        
        // ❌ Solo 100 requests concurrentes debido al pool
        for (Long userId : userIds) {
            futures.add(executor.submit(() -> fetchUserData(userId)));
        }
        
        List<UserData> results = new ArrayList<>();
        for (Future<UserData> future : futures) {
            results.add(future.get()); // ❌ Blocking
        }
        
        return results;
    }
    
    /**
     * ❌ Problema: instanceof + cast manual
     * ✅ Java 21: Pattern matching
     */
    public String processObject(Object obj) {
        if (obj instanceof String) {
            String str = (String) obj;  // ❌ Cast manual
            return "String: " + str.toUpperCase();
        } else if (obj instanceof Integer) {
            Integer num = (Integer) obj;  // ❌ Cast manual
            return "Number: " + (num * 2);
        } else if (obj instanceof List) {
            List<?> list = (List<?>) obj;  // ❌ Cast manual
            return "List size: " + list.size();
        }
        return "Unknown";
    }
    
    /**
     * ❌ Problema: Switch con breaks
     * ✅ Java 21: Switch expression
     */
    public String getDayType(DayOfWeek day) {
        String result;
        switch (day) {
            case MONDAY:
            case TUESDAY:
            case WEDNESDAY:
            case THURSDAY:
            case FRIDAY:
                result = "Weekday";
                break;
            case SATURDAY:
            case SUNDAY:
                result = "Weekend";
                break;
            default:
                result = "Unknown";
        }
        return result;
    }
    
    /**
     * ❌ Problema: POJO inmutable verbose
     * ✅ Java 21: Record (1 línea)
     */
    public static class Point {
        private final int x;
        private final int y;
        
        public Point(int x, int y) {
            this.x = x;
            this.y = y;
        }
        
        public int getX() { return x; }
        public int getY() { return y; }
        
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof Point)) return false;
            Point point = (Point) o;
            return x == point.x && y == point.y;
        }
        
        @Override
        public int hashCode() {
            return Objects.hash(x, y);
        }
        
        @Override
        public String toString() {
            return "Point{x=" + x + ", y=" + y + '}';
        }
    }
    
    /**
     * ❌ Problema: Acceso manual a primer/último elemento
     * ✅ Java 21: list.getFirst() / getLast()
     */
    public void processFirstAndLast(List<String> items) {
        if (!items.isEmpty()) {
            String first = items.get(0);  // ❌ Verbose
            String last = items.get(items.size() - 1);  // ❌ Verbose
            
            System.out.println("First: " + first);
            System.out.println("Last: " + last);
        }
    }
    
    /**
     * ❌ Problema: Iteración reversa manual
     * ✅ Java 21: list.reversed()
     */
    public void reverseIteration(List<Integer> numbers) {
        for (int i = numbers.size() - 1; i >= 0; i--) {
            process(numbers.get(i));
        }
    }
    
    /**
     * ❌ Problema: ThreadLocal requiere cleanup manual
     * ✅ Java 21: ScopedValue con auto-cleanup
     */
    public void handleRequest(User user) {
        currentUser.set(user);
        try {
            processRequest();
        } finally {
            currentUser.remove();  // ❌ Fácil olvidar!
        }
    }
    
    /**
     * ❌ Problema: String.format verbose
     * ✅ Java 21: String Templates
     */
    public String formatUserMessage(String name, int points, double balance) {
        return String.format(
            "User %s has %d points and $%.2f balance",
            name, points, balance
        );  // ❌ Índices fáciles de equivocar
    }
    
    /**
     * ❌ Problema: Concatenación multilínea
     * ✅ Java 21: Text Blocks
     */
    public String generateHTML(String title, String content) {
        return "<html>\n" +
               "  <head>\n" +
               "    <title>" + title + "</title>\n" +
               "  </head>\n" +
               "  <body>\n" +
               "    <h1>" + title + "</h1>\n" +
               "    <p>" + content + "</p>\n" +
               "  </body>\n" +
               "</html>";
    }
    
    /**
     * ❌ Problema: CompletableFuture complejo
     * ✅ Java 21: Structured Concurrency
     */
    public UserProfile fetchUserProfile(Long userId) throws Exception {
        CompletableFuture<User> userFuture = 
            CompletableFuture.supplyAsync(() -> fetchUser(userId), executor);
        
        CompletableFuture<Orders> ordersFuture = 
            CompletableFuture.supplyAsync(() -> fetchOrders(userId), executor);
        
        CompletableFuture<Preferences> prefsFuture = 
            CompletableFuture.supplyAsync(() -> fetchPreferences(userId), executor);
        
        try {
            User user = userFuture.get();
            Orders orders = ordersFuture.get();
            Preferences prefs = prefsFuture.get();
            
            return new UserProfile(user, orders, prefs);
        } catch (Exception e) {
            // ❌ ¿Qué pasa con tareas que aún corren?
            throw new RuntimeException(e);
        }
    }
    
    /**
     * ❌ Problema: Collections.unmodifiableList verbose
     * ✅ Java 21: List.of()
     */
    public List<String> getImmutableList() {
        return Collections.unmodifiableList(
            new ArrayList<>(Arrays.asList("a", "b", "c"))
        );  // ❌ Muy verbose
    }
    
    /**
     * ❌ Problema: Jerarquía abierta sin control
     * ✅ Java 21: Sealed classes
     */
    public static abstract class Shape {
        abstract double area();
        // ❌ Cualquiera puede extender Shape
    }
    
    public static class Circle extends Shape {
        private final double radius;
        
        public Circle(double radius) {
            this.radius = radius;
        }
        
        @Override
        double area() {
            return Math.PI * radius * radius;
        }
    }
    
    // Helper methods y clases
    private UserData fetchUserData(Long userId) {
        return new UserData();
    }
    
    private User fetchUser(Long userId) {
        return new User();
    }
    
    private Orders fetchOrders(Long userId) {
        return new Orders();
    }
    
    private Preferences fetchPreferences(Long userId) {
        return new Preferences();
    }
    
    private void processRequest() {}
    private void process(int num) {}
    
    enum DayOfWeek {
        MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
    }
    
    static class User {}
    static class UserData {}
    static class Orders {}
    static class Preferences {}
    static class UserProfile {
        UserProfile(User u, Orders o, Preferences p) {}
    }
}