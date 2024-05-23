/** @type {import('@maizzle/framework').Config} */
const jsonData = require("./data.json");
const tailwindConfig = require("./tailwind.config.js");
const output = require("./output.json");

/*
|-------------------------------------------------------------------------------
| Development config                      https://maizzle.com/docs/environments
|-------------------------------------------------------------------------------
|
| The exported object contains the default Maizzle settings for development.
| This is used when you run `maizzle build` or `maizzle serve` and it has
| the fastest build time, since most transformations are disabled.
|
*/

module.exports = {
  build: {
    templates: {
      source: "src/templates",
      destination: {
        path: "build_local",
      },
      assets: {
        source: "src/images",
        destination: "images",
      },
    },
  },
  css: {
    inline: true,
    tailwind: {
      config: tailwindConfig,
    },
  },
  title: "Weekly Meal Plan - MealPlanIQ",
  urlAddress: "https://mealplaniq-may-2024.uw.r.appspot.com",
  imageUrl: "https://storage.googleapis.com/mealplaniq-may-2024-recipe-images",
  data: {
    shoppingList: jsonData.shopping_list,
    plans: output.days,
    nutrition: output.tableData,
    user: jsonData.user,
    lastDate: jsonData.meal_plan[jsonData.meal_plan.length - 1].date,
  },
};
