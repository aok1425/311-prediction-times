# Investigating fairness in Boston 311 city services

311 is the number you can call to have the city fix a pothole, remove grafitti, or [retrieve keys from a public trash container](https://www.bostonglobe.com/opinion/letters/2015/12/30/boston-service-really-works/9qzMXKQifIHK85cwUxgnxL/story.html). Since Boston launched its 311 service in [2015](https://www.bostonglobe.com/metro/2015/08/11/boston-launches-non-emergency-hotline/fKZXUvQ33PLFhyZ5nF5e7H/story.html) along with public performance data, it offers one of the most concrete ways to hold the city accountable.

I investigate the fairness of 311 performance by socioeconomic factors, and then look at the corollary: civic participation in the 311 program.

![q2_map](http://i.imgur.com/YSucwbD.png)

## Methods

I retrieved 5+ years worth of 311 data from [Boston's data portal](https://data.cityofboston.gov/City-Services/311-Service-Requests/awu8-dc52), totaling 900,000+ rows. I retrieved socioeconomic data from the Census.

These are 2 sample rows from my dataset, transposed:
![q2_sample_rows](http://i.imgur.com/Hl40EL8.png)

I grouped categories of rows together, because the process and factors to complete 311 issues differs by the category of job.

## Results
For the five groups of categories I looked at, I most notably found that a higher proportion of Hispanics was associated with worse performance:

![q2_results](http://i.imgur.com/pN8LxDI.png)

<SES confounds w sth else, I bet>

## Data caveats/data cleaning
- negative y values
- invalid issues by closure reason
- issues that last too long; 3 SDs
- pothole, needle pickup not associated