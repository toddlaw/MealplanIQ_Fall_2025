/** @type {import('@maizzle/framework').Config} */
const jsonData = require("./data.json");
const tailwindConfig = require("./tailwind.config.js");

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
  urlAddress: "https://mealplaniq-may-2024.uw.r.appspot.com",
  imageUrl:
    "https://storage.cloud.google.com/mealplaniq-may-2024-recipe-images",
  data: {
    shoppingList: jsonData.shopping_list,
    plans: jsonData.meal_plan,
    nutrition: jsonData.nutrition,
    user: jsonData.user,
    lastDate: jsonData.meal_plan[jsonData.meal_plan.length - 1].date,
  },
};
