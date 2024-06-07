<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://cdn3.iconfinder.com/data/icons/databases-3/512/search_data-512.png" alt="search database logo"></a>
</p>

<h3 align="center">Service Content Searching</h3>

---

<p align="center"> Content Searching Relevant Data With Question
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Features](#features)
- [Getting Started](#getting_started)
- [Running the tests](#tests)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)
- [Authors](#authors)
- [VERSION](#version)

## 🧐 About <a name = "about"></a>

**The Content Searching Relevant Data With Question** project aims to facilitate the search for relevant data by interpreting natural language questions. It uses advanced algorithms to understand the context and intent behind a question, providing users with precise and relevant information.

### Key Objectives
- **Improve Search Accuracy:** Enhance the precision of search results by understanding the context and semantics of user queries.
- **Optimize Performance:** Ensure that the search process is efficient and can handle large volumes of data without significant delays.
- **Scalability:** Design the system to be scalable, allowing it to manage increasing amounts of data and more complex queries over time.
- **Integration:** Enable easy integration with existing data sources and systems, ensuring seamless adoption and use.

## 🏁 Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

Make sure you have the following software installed:

- [GitHub Project](https://github.com/suthipongg/Service-content-searching.git)
- [Semantic search](https://github.com/Nawaphong-13/Service-sentence-extractor.git)
- [Re-Ranking API](https://github.com/suthipongg/Service-re-ranking.git) (Optional)
- [pm2](https://pm2.keymetrics.io/docs/usage/quick-start/)

### Installing

1. Clone this GitHub repository:
  ```bash
  git clone https://github.com/suthipongg/Service-content-searching.git
  ```

2. Create a virtual environment:
  ```bash
  python3 -m venv venv
  ```

3. Activate the virtual environment:
  ```bash
  # For Linux
  source venv/bin/activate
  ```

4. Install the required packages from the requirements file:
  ```bash
  pip install -r requirements.txt
  ```

## 🔧 Running the tests <a name = "tests"></a>

To run the automated tests for this system, follow these steps:

1. Navigate to the GitHub project directory:
  ```bash
  cd test_api
  ```

2. Run test for the GitHub project:
  ```bash
  bash test_api.bash 
  ```

## 🎈 Usage <a name="usage"></a>

To use the system, follow these steps:

1. **Run the application:**
  ```bash
  bash start_pm2.sh
  ```

2. **Access the application:**
    Open your browser and navigate to `http://localhost:8092`

This section provides clear instructions for running the UVicorn servers for this project. Adjust it as needed based on your project's specifics.

## 🚀 Deployment <a name = "deployment"></a>

1. **Server Setup**: Set up a server environment suitable for hosting your project. This typically involves choosing a cloud provider and provisioning a virtual machine instance.

2. **Software Installation**: Install the necessary software dependencies on your server, including Python. Follow the installation instructions provided by the respective software vendors.

3. **Clone Repository**: Clone the GitHub repository containing your project onto your server using the `git clone` command.

4. **Environment Configuration**: Set up environment variables and configuration files as needed for your project. Ensure that sensitive information such as API keys and database credentials are securely stored.

5. **Build and Install**: Build your project and install any required dependencies using the appropriate package manager (e.g., pip for Python projects). You may also need to compile any frontend assets if applicable.

6. **Run Servers**: Start the necessary servers for your project, such as UVicorn for running your web application and any other backend services (e.g., Elasticsearch, MongoDB, Redis).

## ⛏️ Built Using <a name = "built_using"></a>

This project is built using the following technologies:

- [Python](https://www.python.org/) - Programming language
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework for building APIs with Python

These technologies were chosen for their performance, scalability, and ease of use, enabling us to build a robust and efficient system for our project.

<details>
<summary>Version</summary>

# Version History

## [0.0.0] (2024-06-07)

- Release date: June 7, 2024

### Added
- Initial release of the project.

</details>