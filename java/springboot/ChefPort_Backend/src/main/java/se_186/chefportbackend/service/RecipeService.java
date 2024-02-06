package se_186.chefportbackend.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import se_186.chefportbackend.model.User;
import se_186.chefportbackend.repository.RecipeRepository;
import se_186.chefportbackend.model.Recipe;
import se_186.chefportbackend.repository.UserRepository;

@Service
public class RecipeService {
    private final RecipeRepository repo;

    public RecipeService(RecipeRepository repo){
        this.repo = repo;
    }

    public Recipe[] getRecipes(String recipeName){
        return repo.findAllByRecipeName(recipeName).toArray(new Recipe[0]);

    }

    public Recipe createRecipe(Recipe recipe) {

        return repo.save(recipe);

    }


}


