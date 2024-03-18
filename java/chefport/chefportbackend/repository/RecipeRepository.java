package se_186.chefportbackend.repository;

import se_186.chefportbackend.model.Recipe;
import java.util.List;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface RecipeRepository extends MongoRepository<Recipe, String>{
    public List<Recipe> findAllByRecipeName(String recipeName);

}
