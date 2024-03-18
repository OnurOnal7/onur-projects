
package se_186.chefportbackend.repository;

import java.util.List;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.repository.MongoRepository;
import se_186.chefportbackend.model.User;


public interface UserRepository extends MongoRepository<User, String>{

    public User findByUsername(String username);

}
