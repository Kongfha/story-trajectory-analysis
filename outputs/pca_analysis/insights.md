# PCA Component Insights (Global + Book)

## Corpus-Level Component Diagnostics
- PC1 explained_variance_ratio=0.0719 | cumulative=0.0719
- PC2 explained_variance_ratio=0.0650 | cumulative=0.1369
- PC3 explained_variance_ratio=0.0385 | cumulative=0.1754
- PC4 explained_variance_ratio=0.0312 | cumulative=0.2066
- PC5 explained_variance_ratio=0.0300 | cumulative=0.2366

## Component Semantics (Exemplar-Based)
- PC1:
  + positive exemplar: 1184 | The Count of Monte Cristo | score=0.526 | shore of the Mediterranean. If Bonaparte landed at Naples, the whole coalition would be on foot before he could even reach Piombino; if he l
  + positive exemplar: 1184 | The Count of Monte Cristo | score=0.524 | my honor,’ replied M. de Villefort; ‘they fancy that their countryman is still emperor. You have mistaken the time, you should have told me 
  - negative exemplar: 16 | Peter Pan | score=-0.447 | up.” “Were not the leaves at the foot of the window, mother?” It was quite true; the leaves had been found very near the window. Mrs. Darlin
  - negative exemplar: 16 | Peter Pan | score=-0.432 | or the only available tree is an odd shape, Peter does some things to you, and after that you fit. Once you fit, great care must be taken to
- PC2:
  + positive exemplar: 1342 | Pride and Prejudice | score=0.513 | I go on I shall displease you by saying what I think of persons you esteem. Stop me, whilst you can.” “You persist, then, in supposing his s
  + positive exemplar: 1342 | Pride and Prejudice | score=0.506 | and whose astonishment at being so addressed was very evident. Her cousin prefaced his speech with a solemn bow, and though she could not he
  - negative exemplar: 36 | The War of the Worlds | score=-0.552 | the end. It was dropping off in flakes and raining down upon the sand. A large piece suddenly came off and fell with a sharp noise that brou
  - negative exemplar: 521 | Robinson Crusoe | score=-0.542 | a W. and by S. sun, or thereabouts, which, in those countries, is near the setting. Before I set up my tent I drew a half-circle before the 
- PC3:
  + positive exemplar: 1661 | The Adventures of Sherlock Holmes | score=0.482 | “S. H. for J. O.” Then he sealed it and addressed it to “Captain James Calhoun, Barque _Lone Star_, Savannah, Georgia.” “That will await him
  + positive exemplar: 103 | Around the World in Eighty Days | score=0.452 | captain forgot in an instant his anger, his imprisonment, and all his grudges against his passenger. The “Henrietta” was twenty years old; i
  - negative exemplar: 84 | Frankenstein; Or, The Modern Prometheus | score=-0.410 | of my dead mother in my arms; a shroud enveloped her form, and I saw the grave-worms crawling in the folds of the flannel. I started from my
  - negative exemplar: 345 | Dracula | score=-0.409 | he may baffle us for years; and in the meantime!--the thought is too horrible, I dare not think of it even now. This I know: that if ever th
- PC4:
  + positive exemplar: 521 | Robinson Crusoe | score=0.482 | yet come to the pitch of hardness to which it has since, reproached me with the contempt of advice, and the breach of my duty to God and my 
  + positive exemplar: 521 | Robinson Crusoe | score=0.453 | myself; and if I should not fall into their hands, what I should do for provision, or whither I should bend my course; none of these thought
  - negative exemplar: 175 | The Phantom of the Opera | score=-0.422 | must reach Christine at all costs. He therefore went on his knees also and hung from the trap with both hands. "Let go!" said a voice. And h
  - negative exemplar: 35 | The Time Machine | score=-0.414 | hurry on ahead!” “To discover a society,” said I, “erected on a strictly communistic basis.” “Of all the wild extravagant theories!” began t
- PC5:
  + positive exemplar: 55 | The Wonderful Wizard of Oz | score=0.401 | Dorothy, clapping her hands. “Oh, let us start for the Emerald City tomorrow!” This they decided to do. The next day they called the Winkies
  + positive exemplar: 55 | The Wonderful Wizard of Oz | score=0.373 | a winged laugh; “but as we have a long journey before us, I will pass the time by telling you about it, if you wish.” “I shall be glad to he
  - negative exemplar: 1661 | The Adventures of Sherlock Holmes | score=-0.445 | the body was eventually recovered. It proved to be that of a young gentleman whose name, as it appears from an envelope which was found in h
  - negative exemplar: 1661 | The Adventures of Sherlock Holmes | score=-0.442 | beast. His cry brought back his son; but I had gained the cover of the wood, though I was forced to go back to fetch the cloak which I had d

## Book-Level Highlights
Highest PCA trajectory volatility (mean_speed):
- 345 | Dracula | mean_speed=0.1426 | p95_speed=0.2523
- 84 | Frankenstein; Or, The Modern Prometheus | mean_speed=0.1421 | p95_speed=0.2623
- 175 | The Phantom of the Opera | mean_speed=0.1362 | p95_speed=0.2490

Strongest PCA-speed / acceleration coupling (k=7):
- 768 | Wuthering Heights | corr_speed_a=0.4642 | corr_speed_s=0.3766
- 1342 | Pride and Prejudice | corr_speed_a=0.3879 | corr_speed_s=0.3471
- 1513 | Romeo and Juliet | corr_speed_a=0.3427 | corr_speed_s=0.3857

Most atypical temporal component trends (|corr(PC, position)|):
- 43 | The Strange Case of Dr. Jekyll and Mr. Hyde | PC4 corr=0.5632 | q=0.0014
- 1513 | Romeo and Juliet | PC5 corr=-0.5549 | q=0.0015
- 175 | The Phantom of the Opera | PC2 corr=-0.5012 | q=0.0022

## Sensitivity Across k = 5, 7, 11
- k=5: median corr_speed_s=0.3819, median corr_speed_a=0.2358
- k=7: median corr_speed_s=0.3214, median corr_speed_a=0.2597
- k=11: median corr_speed_s=0.2544, median corr_speed_a=0.2670

## Caveats
- PCA components are derived from embedding geometry and require semantic triangulation with text exemplars.
- Association metrics are correlational and do not establish causal narrative mechanisms.
- Missing/invalid signal artifacts are skipped and logged in integrity tables.

