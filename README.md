# RESTful API Creation

## Table Creation and Initialization

- After initializing a new Flask app, configuring the database, and creating a Base class, we also init SQLAlchemy and Marshmallow.

- SQLAlchemy orm helps us with table creation, mapping our relationships and each tables column attributes. For example, using our Base class we create a users table.

- User has a one-to-many relationship with Order, Order has a many-to-one relationship with User, and Order and Product have a many-to-many realtionship.

## Marshmallow

- When we initialize the Marshmallow schemas, we init a schema that can return one object, and also one that can serialize many objects. We do this for each table.

## Endpoints wIth Flask

- When we use a GET method to return objects, we either select all users or pass an id (pk) to select just one object. We pass a 200 code to the user which means everything worked.

- When we use a POST method we have to use a try/except block to ensure the user has passed valid data. If not, a 400 errror message is returned. If everything is correct we create the object with proper object attributes. If the database is expecting a name, address, and email- it needs all those attributes.

- When we use a PUT method, we have to pass id to ensure we are selecting the right object. After getting the id, if it doesn't belong to that object, a 400 code is created. Also, just like POST we need to ensure the updated data is valid. If everything checks out, we commit it to the database.

- When we use a DELETE, we also have to pass id to make sure we are deleting the correct object. After getting the id, and validating data, we delete the object. Since we can't return that object, we return a message.
