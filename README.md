# Web scraping and analysis
This project aims to extract data from the sports stats website sofascore.com to analyse the predictive ability of users' guesses about sport events. In particular, sofascore.com provides a tool that allows users to make predictions about the outcome of sport events. In addition, it provides the closing odds offered by a bookmaker and the outcome of the event. All this information is loaded to the website thorugh Java Script and it can be accessed through the use of APIs. Using Python and http.client the APIs were accessed and the relevant information for all tennis matches from the 1st of January 2024 till the 3rd of June 2024 was stored in a dataframe. The data consists of 105110 matches and contains names of the players, outcome, timestamp, match id, user votes and odds for player 1 victory and for player 2 victory. 

## Probabilities implied by votes Vs Probabilities implied by odds

The analysis of the data was conducted by considering only the events that presented a number of users' votes larger than 500. The resulting data was used to calculate the probabilities implied by the votes and the probabilities implied by the odds. Then, it was divided into bins based on the probability implied by votes to obtain an estimate of the probability density implied by votes. The same procedure was performed for the probability implied by odds. Finally, both types of probabilities were compared to their corresponding bins to measure which source produced the more accurate probabilities.

Results showed that closing odds are more successfull at estimating the probability of outcomes for tennis matches than users' guesses.

## Do votes shift odds from real probabilities?

The hypothesis is that, for some events, a considerable amount of 'wrong' guesses forces bookmakers to separate odds from the real probabilities of an event. This scenario would create the opportunity to bet againts the votes and generate a positive profit. 

Results show that, by increasing the number of total votes and the discrepancy between probabilities implied by votes and probabilities implied by odds, it is possible to achieve positive returns and beat the bookmakers.

![](/images/profit_per_bet)
