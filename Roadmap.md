# Roadmap

## Overview

1. Gathering and Data Cleaning
2. Analysis
3. Documentation
4. Integration on Website
   - Caching coingecko data
5. Update Mechanism and Accessibility


## Gathering

Gathering requires scripts that scrape data or pull data via some api. Subsequently the data needs to be cleaned or made usable for analysis and cached into some semi-persistent manner. 

Workpackages:
- [x] 1.1 Create a data acquisition class, that handles the api requests from coingecko and potentially other sources. (~ 2 hour)
- [ ] 1.2 Include some updating mechanism for new data. (~ 1 hour)
- [ ] 1.3 Adjust for new data sources.  (~ 1 hour)
- [ ] 1.4 Create scripts that scrape data {not needed at the moment}. (~ 1 hour)


## Analysis

We divide the analysis into three types of stablecoins:
- fiat-backed and hybrid
- purely crypto-backed
- algorithmic

They all share basic risk metrics, but each type carries different risks and thus requires their own analysis. [Some open source risk packages](https://www.tradingview.com/scripts/risk/).

Workpackages:
- [ ] 2.1 Make a list of basic shared risk metrics. (~ 3 hours)
- [ ] 2.2.1 Look at one representative for a purely fiat-backed stablecoin and identify risks. Use Tether here. (~ 3 hours)
- [ ] 2.2.2 Look at one representative for a single or multi-collateral purely crypto-backed stablecoin and identify risks. Use Dai here. (~ 5 hours)
- [ ] 2.2.3 Look at one representative for an algorithmic crypto stablecoin and identify risks. Use Ampleforth (LUNA) or Dynamic Set Dollar (DSD). Beforehand do a bit if research on both of them to figure out which one has better data. (~ 5 hours)
- [ ] 2.3 Investigate basic shared risk metrics, like *Average return rate to peg* or *weighted volatility measure* that pertain to all stablecoins irrespective of their type. Make this a case study for one particular stable coin, i.e. pick USDC. (~ 2 hours)
- [ ] 2.4 Run the basic shared risk metrics for all coins in the list (c.f. section 2.1). (~ 3 hours)
- [ ] 2.5 Advanced analysis. This is research in progress and before engaging into any direction there should be some sort of consensus:
   - Anomaly detection via clustering algorithms. (~ depends )
   - Training a neural net with labelled data on crashes. (~ depends )


## Documentation

The documentation contains two parts. 1) Presenting the results from the Analysis on a high and low level (involving the time-series analysis, and some plots, possibly interactive) html-based format. 2) Documenting the scripts that generate the analysis.

Workpackages:
- [ ] 3.1 Create a template reporting format (pandas, plotly or datapane). (~ 1 hour)
- [ ] 3.2 Research on how to properly present the risk analysis. (~ 3 hours)
- [ ] 3.3 Fill out the high level risk analysis. (~ 2 hours)
- [ ] 3.4 Discuss some coins in detail. (~ 1 + 1/(coin) hours per coin, where the effort probably decreases with additional coins)
- [ ] 3.5 Add detailed analysis section. (~ 2-3 hours)
- [ ] 3.6 Show a data table, where one can filter the risks for all sorts of stablecoins. (~ 2-3 hours)


## Web-Integration

The results should be presented on the popcorn DAO page.

Workpackages:
- [ ] 4.1 Sync up with the frontend people to agree on integration path. (~ 2 hours)
- [ ] 4.2 Migrate into main repo and merge. (~ 2 hours)
- [ ] 4.3 Updating mechanism and caching data into database or persisting it in any other way. (~ 4 hours)
 


## Update Mechanism, Accessibility and Maintenance 

New coins probably need to be added once in a while. Risk metrics need to be refined. New possibly unexpected data needs to be fed. New contributors need to be able to find their way or add new metrics. Maintenance and legacy needs to be addressed.

Workpackages:
- [ ] 5.1 Discuss how to go about maintenance and updating. (~ 0-3 hours)



## Roadmap in Milestones

- [ ] MS1: Set up basic analysis (WP1.1, WP2.1, WP2.2, WP2.3, WP3.1)
- [ ] MS2: Run detailed analysis (WP1.2, WP1.3, WP2.4, WP2.5, WP3.3)
- [ ] MS3: Documentation and Integration (WP3.2, WP3.4, WP3.5, WP3.6, WP4.1, WP4.2)
- [ ] MS4: Maintenance and further analysis (WP1.4*, WP2.5*, WP4.3, WP5.1)

where a * signifies an optional task. 



## Stack

- pandas
- scikit-learn
- pytorch (if needed) 



