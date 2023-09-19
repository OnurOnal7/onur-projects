package se_186.chefportbackend.model;

import org.springframework.data.annotation.Id;


public class Recipe {
    @Id
    public String id;

    private String recipeName;
    private String[] ingridients;
    //, ArrayList<String> ingridients
    public Recipe(String RecipeName, String[] ingridients) {
        this.recipeName = RecipeName;
        this.ingridients = ingridients;
    }

    public String getRecipeName(){
        return recipeName;
    }

    public String[] getIngridients(){
        return ingridients;
    }

    @Override
    public String toString() {
        return String.format(
                "Recipe[id=%s, RecipeName='%s']",
                id, recipeName, ingridients);
    }
}
