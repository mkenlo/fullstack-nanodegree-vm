import catalog

categories = ["Fruits & Vegetables",
              "Bread & Pastries",
              "Milk & Cheese",
              "Meat & Fish",
              "Ingredients and Spices",
              "Frozen & Convenience",
              "Grain Products",
              "Snacks & Sweets",
              "Beverage & Tobacco",
              "HouseHold & Health"]
items = dict()
items["Fruits & Vegetables"] = ["Apples", "Bananas",
                                "Bell pepper", "BlueBerries", "Carrots"]
items["Bread & Pastries"] = ["Bagels", "Bread", "Donuts", "Muffins", "Pie"]
items["Milk & Cheese"] = ["Butter", "Cheese", "Cream", "Cream Cheese", "Milk"]
items["Meat & Fish"] = ["Bacon", "Chicken", "Chicken Breast", "Fish", "Ham"]
items["Ingredients and Spices"] = ["BBQ sauce",
                                   "Balsamic Vinegar", 
                                   "Coconut milk", "Ketchup"]
items["Frozen & Convenience"] = ["Burritos", "Ice cream"]
items["Grain Products"] = ["Cereal", "Rice"]
items["Snacks & Sweets"] = ["Cake", "Candy", "Cookies"]
items["Beverage & Tobacco"] = ["Red Wine"]
items["HouseHold & Health"] = ["Conditionner", "Deodorant", "Dish liquid"]



if __name__ == '__main__':
    # Run Data Insertion
	catalog.deleteAllCategory()
	catalog.deleteAllItems()
	catalog.lofOfItemsCategories(categories, items)