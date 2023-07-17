**Django Dynamic Tables API**

This projects showcases a basic use of the python type function to generate django models on the fly and, Django Schema Editor to create db tables and migrations on runtime. Was implemented as a recruitment task.

**Setup**

Copy `.env_example` to `.env` and set the desired values to env parameters to connect to a postgres database. Leave them unchanged if you want to run the app using docker.

**Standalone run**

Run the following commands to apply initial migrations:

```sh
cd src
python manage.py migrate
```

Afterwards start the app using:

```sh
python manage.py runserver
```

**Docker run**

Start the services (both the `app` and the `postgres`) by running:

```sh
docker compose up -d
```

Run the following commands to apply initial migrations

```sh
docker compose exec app python manage.py migrate
```

**Using the app**

The following endpoints would be available:

- [/](http://localhost:8000): api documentation
- [/swagger](http://localhost:8000/swagger): live testing playground
- [/api](http://localhost:8000/api): api endpoints

**_1. Sample create table request:_**

```
curl --request POST \
  --url http://127.0.0.1:8000/api/table/ \
  --header 'Content-Type: application/json' \
  --data '{
	"name": "Person",
	"fields": {
		"first_name": "string",
		"last_name": "string",
		"age": "integer",
		"address":"string"
	}
}'
```

**_2. Sample falling to update table schema request:_**

```
curl --request PUT \
  --url http://127.0.0.1:8000/api/table/1/ \
  --header 'Content-Type: application/json' \
  --data '{
	"fields": {
		"first_name": "string",
		"last_name": "string",
		"age": "integer",
		"address":"integer"
	}
}'
```

This is because the address field cannot be migrated from string to integer.

**_3. Sample update table schema request:_**

```
curl --request PUT \
  --url http://127.0.0.1:8000/api/table/1/ \
  --header 'Content-Type: application/json' \
  --data '{
	"fields": {
		"first_name": "string",
		"age": "string",
		"address":"string",
		"married": "boolean"
	}
}'
```

**_4. Sample update table schema request:_**

```
curl --request PUT \
  --url http://127.0.0.1:8000/api/table/1/ \
  --header 'Content-Type: application/json' \
  --data '{
	"fields": {
		"first_name": "string",
		"age": "string",
		"address":"string",
		"married": "boolean"
	}
}'
```

**_5. Sample add table row request on initial schema:_**

```
curl --request POST \
  --url http://127.0.0.1:8000/api/table/1/row/ \
  --header 'Content-Type: application/json' \
  --data '{
	"first_name": "Joe",
	"last_name": "Doe",
	"age": 16,
	"address": "Heaven Str 45"
}'
```

**_6. Sample add table row request on modified schema (after request 4.):_**

```
curl --request POST \
  --url http://127.0.0.1:8000/api/table/1/row/ \
  --header 'Content-Type: application/json' \
  --data '{
		"first_name": "Joe",
		"age": "Dow",
		"address": "Hello Street 45",
		"married": true
	}'
```

**_7. Sample retrieve table rows request:_**

```
curl --request GET \
  --url http://127.0.0.1:8000/api/table/11/rows/ \
  --header 'Content-Type: application/json'
```

**App Insights**

The application uses a simple db table (aka reference table) that stores information about the dynamic table id, name and schema (table fields). When a request for creating a new dynamic table is made, an a new entry is saved on the reference table, and afterwards this information is used in order to create a dynamic model. Finally this information is used by the Django schema editor in order to create a real db table.

Whenever a request for updating a dynamic table schema is made, a lookup in the reference table takes place and afterwards this information is used in order to compare the old schema with the new one and apply proper migration on a per field basis

**Future work - Caveats**

1. The supported dynamic table schema is rather simple for now and allows only specifying `integer`, `string` and `boolean` field types. Implementing an additional fields table, with a foreign key on the reference table would allow more complex schema definitions. Also no field options are provided for now, all fields are being created in the db as required and `string` fields allow up to 200 characters.

2. To offer the ability to create dynamic tables with the same name, an \_id postfix is appended in the created db table.

3. Renaming of the dynamic table name is not possible for now.

4. There is no endpoint to retrieve the dynamic table schema for now. On a successful create request the schema is seen under `fields` response property and on a successful update request under `schema` response property.
