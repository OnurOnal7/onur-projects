package ta4_1.MoneyFlow_Backend.Expenses;

import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import ta4_1.MoneyFlow_Backend.Users.UserRepository;
import ta4_1.MoneyFlow_Backend.Users.User;

//import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

/**
 * Controller for managing expenses.
 *
 * @author Kemal Yavuz
 * @author Onur Onal
 *
 */
@RestController
@RequestMapping("/expenses")
public class ExpensesController {
    @Autowired
    private ExpensesRepository expensesRepository;  // Autowire the ExpensesRepository to interact with the database.

    @Autowired
    private UserRepository userRepository;  // Autowire the UserRepository to interact with the User table.

    /**
     * Create or update expenses for a user.
     *
     * @param userId   The ID of the user.
     * @param expenses The expenses object to be created or updated.
     * @return ResponseEntity with the created or updated expenses.
     */
    @PostMapping("/{userId}")
    public ResponseEntity<?> createExpenses(@PathVariable UUID userId, @RequestBody Expenses expenses) {
        Optional<User> userOptional = userRepository.findById(userId);  // Find the user by ID.
        if (!userOptional.isPresent()) {
            return ResponseEntity.notFound().build();   // If the user is not found, return a 404 response.
        }
        User user = userOptional.get();
        expenses.setUser(user); // Set the user for the expenses.
        Expenses savedExpenses = expensesRepository.save(expenses); // Save the expenses to the database.
        user.setExpenses(savedExpenses); // Update the expenses in the User entity
        userRepository.save(user); // Save the updated User entity
        return ResponseEntity.ok(Map.of("userId", expenses.getId()));
    }

    /**
     * Get an expense of a user.
     *
     * @param id The ID of the user.
     * @return ResponseEntity with the found expenses.
     */
    @GetMapping("/{id}")
    public ResponseEntity<Expenses> getExpensesOfUser(@PathVariable UUID id) {
        return userRepository.findById(id)
                .map(user -> ResponseEntity.ok(user.getExpenses()))
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    /**
     * Get all expenses.
     *
     * @return List of all expenses.
     */
    @GetMapping
    public List<Expenses> getAllExpenses() {
        return expensesRepository.findAll();
    }

    /**
     * Update expenses by user ID.
     *
     * @param id             The ID of the user whose expenses to update.
     * @param updatedExpenses The updated expenses object.
     * @return ResponseEntity with the updated expenses.
     */
    @PutMapping("/{id}")
    @Transactional
    public ResponseEntity<Expenses> addExpensesToUser(@PathVariable UUID id, @RequestBody Expenses updatedExpenses) {
        return userRepository.findById(id)
                .map(user -> {
                    Expenses currentExpenses = user.getExpenses();
                    currentExpenses.setPersonal(currentExpenses.getPersonal() + updatedExpenses.getPersonal());
                    currentExpenses.setWork(currentExpenses.getWork() + updatedExpenses.getWork());
                    currentExpenses.setHome(currentExpenses.getHome() + updatedExpenses.getHome());
                    currentExpenses.setOther(currentExpenses.getOther() + updatedExpenses.getOther());

                    return ResponseEntity.ok(currentExpenses); // Return the updated expenses
                })
                .orElseGet(() -> ResponseEntity.notFound().build());
    }


    /*
     * Add extra expenses to a user's existing expenses based on the expense type.
     *
     * @param userId      The ID of the user.
     * @param expenseType The type of expense to add (e.g., "personal", "work", "home", "other").
     * @param amount      The amount to add to the specified expense type.
     * @return ResponseEntity with the updated expenses.
     */
    /*
    @PostMapping("/add/{userId}/{expenseType}")
    public ResponseEntity<Expenses> addExtraExpenses(@PathVariable UUID userId, @PathVariable String expenseType, @RequestBody Double amount) {
        Optional<User> userOptional = userRepository.findById(userId);
        if (!userOptional.isPresent()) {
            return ResponseEntity.notFound().build();
        }
        User user = userOptional.get();
        Expenses expenses = user.getExpenses();
        if (expenses == null) {
            expenses = new Expenses();
            expenses.setUser(user);
        }
        switch (expenseType.toLowerCase()) {
            case "personal":
                expenses.setPersonal(expenses.getPersonal() + amount);
                break;
            case "work":
                expenses.setWork(expenses.getWork() + amount);
                break;
            case "home":
                expenses.setHome(expenses.getHome() + amount);
                break;
            case "other":
                expenses.setOther(expenses.getOther() + amount);
                break;
            default:
                return ResponseEntity.badRequest().body(null);
        }
        Expenses savedExpenses = expensesRepository.save(expenses);
        return ResponseEntity.ok(savedExpenses);
    }
*/
    /**
     * Delete expenses by ID.
     *
     * @param id The ID of the expenses to delete.
     * @return ResponseEntity indicating the result of the deletion.
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteExpenses(@PathVariable UUID id) {
        return expensesRepository.findById(id)
                .map(expenses -> {
                    expensesRepository.delete(expenses);
                    return ResponseEntity.ok().<Void>build();
                })
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}