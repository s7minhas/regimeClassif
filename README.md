# Mining Texts to Efficiently Generate Global Data on Political Regime Types

Authors
---
[Shahryar Minhas](s7minhas.com), [Jay Ulfelder](https://dartthrowingchimp.wordpress.com/), & [Michael D. Ward](https://web.duke.edu/methods/)

Abstract
---
We describe the design and results of an experiment in using text-mining and machine-learning techniques to generate annual measures of national political regime types. Valid and reliable measures of country's forms of national government are essential to cross-national and dynamic analysis of many phenomena of great interest to political scientists, including civil war, interstate war, democratization, and coup d'état. Unfortunately, traditional measures of regime type are very expensive to produce, and observations for ambiguous cases are often sharply contested. In this project, we train a series of support vector machine (SVM) classifiers to infer regime type from textual data sources. To train the classifiers we used vectorized textual reports from Freedom House and the State Department as features for a training set of pre-labeled regime type data. To validate our SVM classifiers, we compare their predictions in an out-of-sample context and the performance results across a variety of metrics (accuracy, precision, recall) are very high. The results of this project highlight the ability of these techniques to contribute to producing real time data sources for use in police science that can also be routinely updated at much lower cost than human-coded data. To this end, we set up a text processing pipeline that pulls updated textual data from selected sources, conducts feature extraction, and applies supervised machine learning methods to produce measures of regime type.
