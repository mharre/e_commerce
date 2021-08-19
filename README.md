# e_commerce
This is my first attempt at creating and delpoying a website completely on my own. There is more focus on the back end functionality than the front end,
even though I tried to design it to the best of my abilities. Front end was created completely with bootstrap. This website is completely fake and used
just as practice for development and deployment.
This website was deployed with AWS on their free tier through elastic beanstalk. I also serve the images separately without the help of Django for better performance.
Use of AWS RDS for my database as well. Because this is the free tier it does take a little time to load everything. 
Most things are designed to be rendered in templates dynamically, lots of templating language, forloops and conditional logic used to try to keep the code DRY.

Functions of the website include:
  1) Landing page with carousel showing some products for "sale"
  2) Ability to browse all products
  3) Ability to filter results of the product based on where they were produced in the world
  4) Ability to search for specific artworks
  5) More details of the artwork itself when clicking on them
  6) Ability to create an account
  7) Ability to login if account is already created
  8) Ability to change login information if desired
  9) Ability to add or remove items from a cart
  10) Ability to delete the item entirely from the cart, or add as much quantity of each item as possible
  11) Detailed checkout summary view
  12) Forms for shipping / billing
  13) Ability to set default shipping / billing addrress
  14) Stripe intergration for payment, just use 42424242... for the credit card details (this is Stripe's testing value, just keep typing 42 over and over)
  15) The ability to add coupons if they are created
  16) Logic to add the total order price and subtract any coupons if necessary
  17) Ability to leave a review on a product in the profile area, but only once the product is "purchased"
  18) With each transaction a reference code is generated as well, which can be seen in "My Orders" once a purchase has been made
  19) Ability to request refund
  20) Email backend to reset a password is in the files but not set up completely as of yet
  21) More things that I cannot think of at the moment!
  22) Additional features to come as I will use this website for more practice in the future
        - I want to add login with email instead of username
        - Review stars based on the average rating 
        - Change aesthetics 
        - More to be added later
