# Stock Indicator Test

## Background
My motivation for this project was to create a reusable test environment to statistically measure the viability of a given trading strategy, the likes of which might be touted by a fanatic YouTuber, an arrogant party guest, or your local barfly. 

In proper nerd fashion, by the power of science, I hope to be able to either: 1) present them with contradictory results in a crowded room, or 2) use the supportive results to achieve world domination, and conveniently forget where the tip came from. Just kidding. I'd make them a Duke or something.

## The Data
- The data was collected from the free tier of the [Alpha Vantage](https://www.alphavantage.co/) API, using the [python wrapper](https://github.com/RomelTorres/alpha_vantage) by Romel Torres.

- Pandas was used for data manipulation, which included:
 - Joining stock prices and their relevant indicators
 - Creating new columns based on the trading conditions for entering and exiting the hypothetical trade.
 - Porting the transformed data to a PostgreSQL Database

- A pipeline script was built to automate the collection of 200 stocks/indicators

## The Trading Conditions


## Statistical Test
### Null hypothesis:
Given specific exit conditions for a stock trade, an indicator **will not** perform better than random chance at predicting a winning entry point. 

### Alternative hypothesis:
Given specific exit conditions for a stock trade, an indicator **will** perform better than random chance at predicting a winning entry point. 

## Results

## Improvements
- Refactor the pipeline script
 - Isolate individual functions to better conform to best practices
 - Add logging
 - Make it easy to plug in different conditions
- Refine the structure of the database
- Create simulations for use in a portfolio subject to trading commissions
