
# Farcaster User Insights

## Overview
Farcaster User Insights is a desktop application designed to provide visual insights into cryptocurrency token holdings and similarities between users within the Farcaster network. This application allows users to search for other users within the network, view detailed visual representations of cryptocurrency holdings, and explore user similarities based on token portfolios.

## Installation

### Prerequisites
Before running the application, ensure that you have Python 3.8 or higher installed on your machine. Additionally, you will need `pip` to install the necessary Python packages.

### Setup
Follow these steps to get the application running on your local machine:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/whalefund/Farcaster_User_Insights.git
   ```
2. **Navigate to the project directory**:
   ```bash
   cd Farcaster_User_Insights
   ```
3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application
To run the application, execute the following command in the project's root directory:
```bash
python gui.py
```
This will launch the graphical user interface, allowing you to interact with the application.

## Usage
Here’s how to use the Farcaster User Insights application:

- **Searching for a User**: Enter the username in the search bar and click the "Search" button. The application will display the user's token portfolio and a list of users with similar portfolios.
- **Viewing Token Details**: Click on any token name displayed in the portfolio list to open a detailed analytics page for that token on an external website.
- **Exploring Similar Users**: The application calculates and displays users similar to the searched user based on their token holdings. You can view detailed profiles of these users by clicking on the "Visit Profile" links provided.

## Data Files
The application relies on two CSV files:
- `aggregated_token_balances_v2.csv`: Contains user token balances.
- `All_Active_Farcaster_Users.csv`: Contains user profile links.

Ensure these files are located in the same directory as `gui.py` or adjust the file paths in the script accordingly.

## Contributions
Contributions to this project are welcome! Please fork the repository, make your changes, and submit a pull request for review.

## License
This project is released under the MIT License. See the LICENSE file in the repository for full details.

## Contact
If you have any questions, suggestions, or contributions, please contact me via email at 548047se@eur.nl or open an issue on this GitHub repository.

