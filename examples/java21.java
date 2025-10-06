package com.example.modern;

import java.util.*;
import java.util.concurrent.*;

/**
 * EJEMPLO: Código Moderno usando Java 21
 * Mismo comportamiento que LegacyCodeExample, pero aprovechando Java 21
 */
public class ModernJava21Example {
    
    // ✅ ScopedValue en lugar de ThreadLocal
    private static final ScopedValue<User> currentUser = ScopedValue.newInstance();
    
    // ✅ Virtual Threads - millones de threads posibles
    private final ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
    
    /**
     * ✅ Virtual Threads permiten millones de requests concurrentes
     * Performance: De ~4K a 1M+ concurrent requests
     */
    public List<UserData> fetchUserDataParallel(List<Long> userIds) 
            throws Exception {
        
        // ✅ Cada userIds.size() threads concurrentes - no limitado por pool
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            List<Subtask<UserData>> tasks = userIds.stream()
                .map(id -> scope.fork(() -> fetchUserData(id)))
                .toList();
            
            scope.join();           // Espera todas
            scope.throwIfFailed();  // Propagate errors
            
            return tasks.stream()
                .map(Subtask::get)
                .toList();
        } // Auto-cleanup de threads
    }
    
    /**
     * ✅ Pattern Matching - más limpio y seguro
     * Beneficio: No más ClassCastException, menos boilerplate
     */
    public String processObject(Object obj) {
        return switch (obj) {
            case String s -> "String: " + s.toUpperCase();
            case Integer i -> "Number: " + (i * 2);
            case List<?> list -> "List size: " + list.size();
            case null -> "Null value";
            default -> "Unknown";
        };
    }
    
    /**
     * ✅ Switch Expression - conciso y exhaustivo
     * Beneficio: Compiler verifica que todos los casos están cubiertos
     */
    public String getDayType(DayOfWeek day) {
        return switch (day) {
            case MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY -> "Weekday";
            case SATURDAY, SUNDAY -> "Weekend";
        };
    }
    
    /**
     * ✅ Record - 1 línea vs 50+ del POJO
     * Auto-genera: constructor, getters, equals, hashCode, toString
     */
    public record Point(int x, int y) {
        // Opcionalmente agregar validación
        public Point {
            if (x < 0 || y < 0) {
                throw new IllegalArgumentException("Negative coordinates");
            }
        }
        
        // Métodos custom opcionales
        public double distanceFromOrigin() {
            return Math.sqrt(x * x + y * y);
        }
    }
    
    /**
     * ✅ Sequenced Collections - API clara y consistente
     * Beneficio: Código más legible
     */
    public void processFirstAndLast(List<String> items) {
        if (!items.isEmpty()) {
            String first = items.getFirst();  // ✅ Clara intención
            String last = items.getLast();    // ✅ Sin cálculos
            
            System.out.println("First: " + first);
            System.out.println("Last: " + last);
        }
    }
    
    /**
     * ✅ reversed() - iteración reversa elegante
     * Beneficio: No más índices manuales
     */
    public void reverseIteration(List<Integer> numbers) {
        for (var num : numbers.reversed()) {
            process(num);
        }
    }
    
    /**
     * ✅ ScopedValue - inmutable y auto-cleanup
     * Beneficio: Imposible olvidar limpiar, thread-safe
     */
    public void handleRequest(User user) {
        ScopedValue.where(currentUser, user)
            .run(() -> processRequest());
        // ✅ Auto-cleanup cuando sale del scope
    }
    
    /**
     * ✅ String Templates (Preview) - natural y type-safe
     * Beneficio: Interpolación directa, sin índices
     */
    public String formatUserMessage(String name, int points, double balance) {
        return STR."User \{name} has \{points} points and $\{balance} balance";
        // ✅ Type-safe, los valores están donde se usan
    }
    
    /**
     * ✅ Text Blocks - strings multilínea legibles
     * Beneficio: Más fácil de leer y mantener
     */
    public String generateHTML(String title, String content) {
        return STR."""
            <html>
              <head>
                <title>\{title}</title>
              </head>
              <body>
                <h1>\{title}</h1>
                <p>\{content}</p>
              </body>
            </html>
            """;
    }
    
    /**
     * ✅ Structured Concurrency - robust error handling
     * Beneficio: Auto-cleanup, mejor manejo de errores
     */
    public UserProfile fetchUserProfile(Long userId) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            // Fork parallel tasks
            Subtask<User> userTask = 
                scope.fork(() -> fetchUser(userId));
            Subtask<Orders> ordersTask = 
                scope.fork(() -> fetchOrders(userId));
            Subtask<Preferences> prefsTask = 
                scope.fork(() -> fetchPreferences(userId));
            
            // Wait for all
            scope.join();
            scope.throwIfFailed();
            
            // ✅ Si una falla, todas se cancelan automáticamente
            return new UserProfile(
                userTask.get(),
                ordersTask.get(),
                prefsTask.get()
            );
        } // ✅ Auto-cleanup de tareas pendientes
    }
    
    /**
     * ✅ List.of() - conciso y eficiente
     * Beneficio: Inmutable por defecto, menos memoria
     */
    public List<String> getImmutableList() {
        return List.of("a", "b", "c");
    }
    
    /**
     * ✅ Sealed Class - control total de jerarquía
     * Beneficio: Pattern matching exhaustivo garantizado
     */
    public sealed interface Shape permits Circle, Rectangle, Triangle {
        double area();
    }
    
    public record Circle(double radius) implements Shape {
        @Override
        public double area() {
            return Math.PI * radius * radius;
        }
    }
    
    public record Rectangle(double width, double height) implements Shape {
        @Override
        public double area() {
            return width * height;
        }
    }
    
    public record Triangle(double base, double height) implements Shape {
        @Override
        public double area() {
            return 0.5 * base * height;
        }
    }
    
    /**
     * ✅ Pattern Matching con Sealed Classes
     * Beneficio: Compiler sabe que cubrimos todos los casos
     */
    public String describeShape(Shape shape) {
        return switch (shape) {
            case Circle c -> STR."Circle with radius \{c.radius()}";
            case Rectangle r -> STR."Rectangle \{r.width()}x\{r.height()}";
            case Triangle t -> STR."Triangle base \{t.base()}, height \{t.height()}";
            // ✅ No need for default - compiler knows all cases
        };
    }
    
    /**
     * ✅ Record Patterns - destructuring directo
     * Beneficio: Extrae valores directamente del pattern
     */
    public double calculateArea(Object obj) {
        return switch (obj) {
            case Circle(double r) -> Math.PI * r * r;
            case Rectangle(double w, double h) -> w * h;
            case Triangle(double b, double h) -> 0.5 * b * h;
            default -> 0.0;
        };
    }
    
    /**
     * ✅ Guarded Patterns - condiciones en el pattern
     * Beneficio: Lógica compleja dentro del switch
     */
    public String classifyCircle(Shape shape) {
        return switch (shape) {
            case Circle(double r) when r < 1.0 -> "Small circle";
            case Circle(double r) when r < 10.0 -> "Medium circle";
            case Circle(double r) -> "Large circle";
            default -> "Not a circle";
        };
    }
    
    /**
     * ✅ Multiple ScopedValues
     * Beneficio: Context propagation thread-safe
     */
    private static final ScopedValue<Locale> currentLocale = ScopedValue.newInstance();
    
    public void handleLocalizedRequest(User user, Locale locale) {
        ScopedValue.where(currentUser, user)
            .where(currentLocale, locale)
            .run(() -> {
                // ✅ Ambos valores disponibles en todo el scope
                processLocalizedRequest();
            });
    }
    
    /**
     * ✅ Virtual Threads con I/O Blocking
     * Beneficio: Blocking I/O es aceptable, escala a millones
     */
    public List<String> fetchMultipleAPIs(List<String> urls) {
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            return urls.stream()
                .map(url -> executor.submit(() -> {
                    // ✅ Blocking HTTP call - OK con virtual threads
                    return httpClient.send(
                        HttpRequest.newBuilder().uri(URI.create(url)).build(),
                        HttpResponse.BodyHandlers.ofString()
                    ).body();
                }))
                .map(future -> {
                    try {
                        return future.get();
                    } catch (Exception e) {
                        return "Error: " + e.getMessage();
                    }
                })
                .toList();
        }
    }
    
    // Helper methods
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
    private void processLocalizedRequest() {}
    private void process(int num) {}
    
    enum DayOfWeek {
        MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
    }
    
    record User() {}
    record UserData() {}
    record Orders() {}
    record Preferences() {}
    record UserProfile(User user, Orders orders, Preferences prefs) {}
    
    private HttpClient httpClient = HttpClient.newHttpClient();
}