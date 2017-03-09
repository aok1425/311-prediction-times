> tl;dr: I investigated fairness in city 311 services (e.g. fixing a pothole) in Boston, and found that an area with a higher proportion of Hispanics was associated with _slower_ completion time.

## Table of Contents

1. [Introduction](#investigating-fairness-in-Boston-311-city-services)
2. [Methods](#methods)
3. [Results](#results)
4. [Caveats](#caveats)
5. [Conclusion](#conclusion) 
6. [Appendix](#appendix)
   * [6.1 Next steps](#next-steps)
   * [6.2 Challenges](#challenges)
   * [6.3 Model performance](#model-performance)

# Investigating fairness in Boston 311 city services

311 is the number you can call to have the city fix a pothole, remove grafitti, or [retrieve keys from a public trash container](https://www.bostonglobe.com/opinion/letters/2015/12/30/boston-service-really-works/9qzMXKQifIHK85cwUxgnxL/story.html). Since Boston launched its 311 service in [2015](https://www.bostonglobe.com/metro/2015/08/11/boston-launches-non-emergency-hotline/fKZXUvQ33PLFhyZ5nF5e7H/story.html) along with public performance data, it offers one of the most concrete ways to hold the city accountable to its citizens.

I investigate the factors associated with 311 completion time, mostly socioeconomic and demographic, but also factors related to city workload.

![q2_map](http://i.imgur.com/YSucwbD.png)

Figure 1. Number of hours to completion for Animal Control issues by Census block group.

## Methods

I retrieved 5+ years worth of 311 data from [Boston's data portal](https://data.cityofboston.gov/City-Services/311-Service-Requests/awu8-dc52), totaling 900,000+ rows. I retrieved socioeconomic data from the Census.

These are 2 sample issues from my dataset, transposed:
![q2_sample_rows](http://i.imgur.com/Hl40EL8.png)

The most detailed level of Census data was by block group, about 6 Boston blocks roughly. Each socioeconomic indicator corresponds to the block group of the issue's location (Figure 1).

I grouped issues by categories (e.g. Request for Snow Plowing and Misc. Snow Complaint), because the process and factors to complete 311 issues differs by category. I looked at 4 specific category groups, since these had many issues, were interesting, and were related to the socioeconomics of the area.

## Results
For the four category groups I looked at, I most notably found that a higher proportion of Hispanics was associated with worse performance:

![q2_results](http://i.imgur.com/tiLVFJJ.png)

Secondly, I found that neither average income nor average years of schooling were statistically significant features. I suspect that if I had taken the race features out, these may have been statistically significant.

Thirdly, I found that socioeconomic diversity in an area is associated with slower service. I suspect that there is a confounding factor involved. Anecdotally, when I saw the areas with the most socioeconomic diversity, they were areas where housing projects are located.

## Caveats

The biggest caveat is trusting the data quality. There were some issues that took 3+ years to complete. Were they finished, or just removed after a period of time? While some completed issues do say, for example, "Administratively Closed", others don't have details. 

I considered the issues that were completed in more than 3 standard deviations away from the mean to be outliers, and removed them from the dataset. Ideally, I would chat with the city staff closing the issues, or have the domain knowledge to know, for example, which of the 3+ years issues to keep, and which to discard.

The second biggest caveat is my category groupings. I chose the categories that on paper look like they would be done by the same department, and involve similar processes (i.e. all categories involving snow plows means the plows would come from the same depots, so they would likely be associated with similar factors). Ideally, I would again chat with city staff to learn the processes for each of the categories, and group the categories accordingly.

## Conclusion

My most notable finding was that a higher proportion of Hispanics in an area is associated with slower 311 completion time, for the four category groups I looked at. One common follow-up question is: by how much? My model is "noisy" enough that I am not confident in the amount, but it is notable that the proportion of Hispanics is always statistically significantly associated with slower completion time, and never faster, than baseline.

Does this mean that city services are biased against Hispanics? Not necessarily. There may be [confounding factors](Model performance) that are associated with both a high proportion of Hispanics and slow completion time. The gold-standard way to control for confounding factors is through experimentation. But since that would be unethical in this context, further observational studies should be done.

On balance, it is troubling that one race consistently has an association with slower completion time across these four categories, and it's a sign that fairness in city 311 services should be looked at more closely, now that we can more easily hold the city accountable with this detailed data.

## Appendix

### Next steps

If I had more time, I would:

- incorporate the additional factors I web scraped for certain categories (e.g. size of the pothole)
- take into account the time series nature of the data (e.g. any trends in completion time over time)

### Challenges

The biggest challenge was in transforming the data and thinking about how to account for data quality issues. The process to add Census data and web-scraped event-level data to my dataset resulted in a 1GB+ file that was too big to save via pickling. It also ran too slowly on my computer, so I had to spin up a high-powered Amazon EC2 instance and analyze the data there.

The data quality issues are tricky without communicating with the people who know how the data is created. Not only were there issues that took too long to complete, there were also issues that finished very quickly (<1 hour). Which of these to remove for my analysis, and which to keep, if I don't have any additional information about them? I ended up keeping them in, thus biasing my completion times downward.

### Model performance

The R2 cores for the test set for Living Conditions and Graffiti Removal were around 10%; Rodents was 4%, and Abandoned Vehicles 1%. These scores mean that the model explain little of the variance of the data.

When looking at the Root Mean Squared Error, a measure of how much our estimate differs from the result,  they are small, about equal to a standard deviation of `y_test`. This could mean that the variance in `y_test` is small, and/or that roughly on average, our estimate doesn't differ much from the result.

Because I was overfitting, by a percentage point or so on R2, I am hesitant to put much confidence in the magnitude of the coefficients. That's why my finding was that in each of the models, one feature was repeatedly statistically significant, and in each case with the same sign. I figured that was the extent to which I could interpret the model results.