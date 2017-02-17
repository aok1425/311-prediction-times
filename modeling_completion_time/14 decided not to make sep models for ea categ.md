I tried it, and found for LassoCV my best R2 was ~0.48, which is less than the 0.54 for all the categories combined.

Why?

My best guess, after running this idea through Moses, is that for the big model, `TYPE` explains much of the variance in the data. But once we split the data by `TYPE`, no other feature explains the variance in the data well for each subset of data.

I can make a DT for each subset of data, and I get better R2 scores than for LassoCV, ~0.5-ish. (RFs anecdotally only add ~2% R2.) But then what can I do with these DTs? I could visualize the trees, but the R2 is so low, I'm not sure I can state the splits with any confidence. I'd have to take the variance of the y range into account.

(If the R2s were good, I was thinking of something like counting the number of times a feature was split on, and noting its depth in the tree, for multiple random DTs for a given category subset of data. This is similar to RF's variable importance, so I would want to read up on that too.)

tl;dr: Since my R2s for the categ subsets are "only" ~0.5-ish, I can make statements only as strong as for the R2 0.54 for the big model. I was hoping the individual R2s would have been better.

Now, the above was in terms of explaining the model.

When it comes to prediction, RMSE is better to look at, and anecdotally the RMSE for subset LassoCVs is better than for the whole dataset LassoCV. Better than RMSE for RFs for all categs. So for prediction, subset models is the way to go.