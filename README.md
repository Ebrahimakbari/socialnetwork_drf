# Social Network DRF

This is a social network web application built using Django and Django REST Framework (DRF) with JWT authentication and email verification.

## Table of Contents

- [Social Network DRF](#social-network-drf)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Technologies Used](#technologies-used)
  - [Installation](#installation)
  - [Usage](#usage)
  - [API Endpoints](#api-endpoints)
  - [Contributing](#contributing)

## Introduction

The Social Network DRF is a platform where users can create posts, like posts, and comment on posts. It provides a RESTful API for easy integration with front-end applications.

## Features

- User authentication and authorization using JWT tokens.
- CRUD operations for posts, comments, and likes.
- Swagger documentation for API endpoints.

## Technologies Used

- Django: A high-level Python web framework.
- Django REST Framework: A powerful and flexible toolkit for building Web APIs.
- PostgreSQL: A relational database management system.
- Docker: A platform for developing, shipping, and running applications.

## Installation

1. Clone the repository to your local machine:

```bash
git clone /home/ebrahim/Desktop/projects/drf/SocialNetwork-drf
```

2. Navigate to the project directory:

```bash
cd SocialNetwork-drf
```

3. Build the Docker containers:

```bash
docker-compose up --build
```

4. Run the migrations:

```bash
docker-compose run web python manage.py migrate
```

5. Create a superuser (optional):

```bash
docker-compose run web python manage.py createsuperuser
```

## Usage

1. Start the application:

```bash
docker-compose up
```

2. Access the application at `http://localhost:8000/`.

3. Access the Swagger documentation at `http://localhost:8000/swagger/`.

## API Endpoints

- Authentication: `/api/auth/`
- Posts: `/api/posts/`
- Comments: `/api/comments/`
- Likes: `/api/likes/`

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Commit your changes.
5. Push to the branch.
6. Create a pull request.