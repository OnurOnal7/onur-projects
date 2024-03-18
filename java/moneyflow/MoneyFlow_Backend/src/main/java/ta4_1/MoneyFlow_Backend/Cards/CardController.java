package ta4_1.MoneyFlow_Backend.Cards;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import ta4_1.MoneyFlow_Backend.Users.User;
import ta4_1.MoneyFlow_Backend.Users.UserRepository;

import java.util.*;

/**
 * Controller for Cards
 *
 * @author Onur Onal
 * @author Kemal Yavuz
 *
 */
@RestController
public class CardController {

    @Autowired
    private CardRepository cardRepository;

    @Autowired
    private UserRepository userRepository;

    /**
     * Retrieves all cards for all users.
     *
     * @return A list of lists containing cards for each user.
     */
    @GetMapping("/cards")
    public List<List<Card>> getAllCards() {
        List<User> users = userRepository.findAll();
        List<List<Card>> allCards = new ArrayList<>();

        for (User u : users) {
            allCards.add(u.getCards());
        }

        return allCards;
    }

    /**
     * Retrieves all cards for a specific user.
     *
     * @param id The UUID of the user.
     * @return A list of cards for the specified user.
     */
    @GetMapping("/cards/userId/{id}")
    public ResponseEntity<List<Card>> getAllCardsOfUser(@PathVariable UUID id) {
        return userRepository.findById(id)
                .map(user -> ResponseEntity.ok(user.getCards()))
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    /**
     * Retrieves a specific card of a user.
     *
     * @param userId The UUID of the user.
     * @param cardId The UUID of the card.
     * @return The card with the specified ID.
     */
    @GetMapping("/cards/id/{userId}/{cardId}")
    public ResponseEntity<Card> getCard(@PathVariable UUID userId, @PathVariable UUID cardId) {
        Optional<User> userOptional = userRepository.findById(userId);
        if (!userOptional.isPresent()) {
            return ResponseEntity.notFound().build();
        }

        User user = userOptional.get();
        List<Card> userCards = user.getCards();

        for (Card c : userCards) {
            if (c.getId().equals(cardId)) {
                return ResponseEntity.ok(c);
            }
        }

        return ResponseEntity.notFound().build();
    }


    /**
     * Retrieves the default card of a specific user.
     *
     * @param id The UUID of the user.
     * @return The card with the specified ID.
     */
    @GetMapping("/cards/userId/{id}/default")
    public ResponseEntity<Card> getDefaultCard(@PathVariable UUID id) {
        Optional<User> userOptional = userRepository.findById(id);

        if (!userOptional.isPresent()) {
            return ResponseEntity.notFound().build();
        }

        User user = userOptional.get();
        List<Card> userCards = user.getCards();

        for (Card c : userCards) {
            if (c.getIsDefault()) {
                return ResponseEntity.ok(c);
            }
        }

        return ResponseEntity.notFound().build();
    }

    /**
     * Creates a new card for a user.
     *
     * @param id   The UUID of the user.
     * @param card The card to be created.
     * @return The UUID of the newly created card.
     */
    @PostMapping("/cards/{id}")
    public ResponseEntity<?> createCard(@PathVariable UUID id, @RequestBody Card card) {
        return userRepository.findById(id)
                .map(user -> {
                    card.setIsDefault(true);
                    List<Card> userCards = user.getCards();

                    for (Card c : userCards) {
                        if (c.getIsDefault() == true) {
                            c.setIsDefault(false);
                            cardRepository.save(c);
                            break;
                        }
                    }

                    card.setUser(user);
                    cardRepository.save(card);
                    user.addCard(card);
                    userRepository.save(user);
                    // Wrap the UUID in a JSON object
                    return ResponseEntity.ok(Map.of("id", card.getId()));

                })
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

/*
    @PutMapping("/cards/{id}")
    public ResponseEntity<Card> updateCard(@PathVariable UUID id, @RequestBody Card card) {
        return cardRepository.findById(id)
                .map(user -> {
                    user.setFirstName(u.getFirstName());
                    user.setLastName(u.getLastName());
                    user.setEmail(u.getEmail());
                    user.setIncome(u.getIncome());
                    user.setPassword(passwordEncoder.encode(u.getPassword()));
                    return ResponseEntity.ok(userRepository.save(user));
                })
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
*/
    /**
     * Deletes a card by its unique ID.
     *
     * @param id the ID of the card to be deleted
     * @return  a success message
     */
    @DeleteMapping("/cards/{id}")
    public ResponseEntity<String> deleteCard(@PathVariable UUID id) {
        return cardRepository.findById(id)
                .map(card -> {
                    cardRepository.deleteById(id);
                    return ResponseEntity.ok("Card deleted successfully");
                })
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}