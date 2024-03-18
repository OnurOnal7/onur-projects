package ta4_1.MoneyFlow_Backend.Users;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import ta4_1.MoneyFlow_Backend.Cards.Card;
import ta4_1.MoneyFlow_Backend.Expenses.Expenses;

import java.util.List;
import java.util.UUID;

/**
 * Provides the Definition/Structure for the user table
 * Represents a User in the MoneyFlow application.
 * Each user has a unique ID, personal information, an income, associated expenses, and a list of cards.
 *
 * @author Onur Onal
 * @author Kemal Yavuz
 *
 */
@Entity // Indicates that this class is an entity in the database.
@Table(name = "users")  // Specifies the table name in the database.
public class User {

    @Id // Indicates that this field is the primary key.
    @GeneratedValue(generator = "UUID") // Specifies that the ID should be generated automatically as a UUID.
    private UUID id; // Unique identifier for the user.

    @Column(name = "first_name", nullable = false)  // Maps this field to the "first_name" column in the database.
    private String firstName;   // The user's first name.

    @Column(name = "last_name", nullable = false)   // Maps this field to the "last_name" column in the database.
    private String lastName;    // The user's last name.

    @Column(name = "password", nullable = false)    // Maps this field to the "password" column in the database.
    private String password;    // The user's password.

    @Column(name = "email", unique = true, nullable = false)    // Maps this field to the "email" column in the database.
    private String email;   // The user's email.

    @Column(name = "type")  // Maps this field to the "type" column in the database.
    private String type;    // The user's type (e.g., regular, premium).

    @Column(name = "income")    // Maps this field to the "income" column in the database.
    private Double income;  // The user's income.

    @OneToOne(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)   // Establishes a one-to-one relationship with the Expenses entity.
    private Expenses expenses;  // The user's associated expenses.

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)  // Establishes a one-to-many relationship with the Card entity.
    private List<Card> cards;   // The user's associated cards.

    /**
     * Default constructor for JPA.
     */
    public User(){

    }

    /**
     * Constructs a new User with the specified personal information and income.
     *
     * @param firstName - the first name of the user
     * @param lastName  - the last name of the user
     * @param password  - the password of the user
     * @param email - the email of the user
     * @param income    - the income of the user
     */
    public User(String firstName, String lastName, String password, String email, double income){
        this.firstName = firstName;
        this.lastName = lastName;
        this.password = password;
        this.email = email;
        this.income = income;
    }

    // Getters and setters for each field

    public String getFirstName() {
        return this.firstName;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public String getLastName() {
        return this.lastName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public String getPassword() {
        return this.password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getEmail() {
        return this.email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public UUID getId() {
        return this.id;
    }

    public void setId() {
        this.id = UUID.randomUUID();
    }

    public String getType() { return this.type; }

    public void setType(String type) { this.type = type; }

    public Double getIncome() {
        return income;
    }

    public void setIncome(Double income) {
        this.income = income;
    }

    public List<Card> getCards() { return this.cards; }

    public void addCard(Card card) {
        if (cards != null) {
            this.cards.add(card);
            card.setUser(this);
        }
    }

    public Expenses getExpenses() {
        return expenses;
    }

    public void setExpenses(Expenses expenses) {
        this.expenses = expenses;
        if (expenses != null) {
            expenses.setUser(this); // Set the user in the Expenses entity
        }
    }

    /**
     * Generates a financial report for the user, summarizing their income, expenses, and remaining budget.
     *
     * @return  Budget = Income - Expenses
     */
    public double generateBudget() {
        double totalExpenses = expenses != null ? expenses.getTotalExpenses() : 0;
        return income - totalExpenses;
    }

    /**
     * Represents the user as a string containing their ID, personal information, and income.
     *
     * @return  a string representation of the user
     */
    @Override
    public String toString() {
        return id + " "
                + firstName + " "
                + lastName + " "
                + password + " "
                + email + " "
                + income + " "
                + type;
    }
}