# Code for Paper *An Experimental View on Committees Providing Justified Representation*

This repository contains code and experimental data for reproducing the
experiments, plots, and figures from the paper _An Experimental View on
Committees Providing Justified Representation_.

The code was created by [Andrzej Kaczmarczyk](https://akaczmarczyk.com).

The project is part of the [PRAGMA project](https://home.agh.edu.pl/~pragma/)
which has received funding from the [European Research Council
(ERC)](https://home.agh.edu.pl/~pragma/) under the European Union’s Horizon 2020
research and innovation programme ([grant agreement No
101002854](https://erc.easme-web.eu/?p=101002854)). 


## Experiments in Paper

**xJR Probability**: Section 3, Figure 2

**Average Minimum Justified Groups**: Section 4, Figure 4

**Hitmaps and Heatmaps**: Section 5, Figures 5 and 6

## Setup

Install all dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

The required datasets are already included in the `dataset/` directory

> **_NOTE:_**  The repository contains the results of experiments because
> computing them is a computationally heavy task. This is why this readme starts
> with the instructions for plotting the experiments' outcome first. The
> instructions for running the experiments follow later.

---

## Plotting Experiments

### xJR Probability Charts

To plot the probability of obtaining an xJR committee.

* Output directory: `exp_results/xJR_prob/pics`
* Run:

```bash
./exp_results/xJR_prob/draw_all.sh
```

---

### Average Minimum Justified Groups

To plots the average sizes of minimum justified groups.

* Output directory: `exp_results/min_justified/pics`
* Run:

```bash
./exp_results/min_justified/draw_all_paper_min_xjr.sh
```

#### Combined Overview (not in paper)

To create a PNG with all pabulib averages (contains label glitches):

* Output file: `exp_results/min_justified/pics/pabulib_all_13.png`
* Run:

```bash
./exp_results/min_justified/draw_jammed_pabulib.sh
```

---

### Hitmaps

To plot hitmaps for Pabulib and synthetic cultures.


* Output directory: `exp_results/hitmap/pics`
* Run:

```bash
./exp_results/hitmap/draw_all_pabulib.sh
./exp_results/hitmap/draw_all_cultures.sh
```


#### Combined Overview (not in paper)

To create a PDF combining all hitmaps (without full descriptions):

* Output file: `exp_results/hitmap/jammed.pdf`
* Run:

```bash
./exp_results/heatmap/jampictures.sh
```

---

### 4. Heatmaps

To plot heatmaps for Pabulib and synthetic cultures.

* Output directory: `exp_results/heatmap/pics`
* Run:

```bash
./exp_results/heatmap/draw_pabulib.sh
./exp_results/heatmap/draw_cultures.sh
```

#### Combined Overview (not in paper)

To create a PDF with all Pabulib heatmaps (descriptions missing):

* Output file: `exp_results/heatmap/jammed.pdf`
* Run:

```bash
./exp_results/heatmap/jampabulib.sh
```

---

## Recomputing Experiments

> **Warning**: Recomputing experiments is computationally intensive and may
> take days or even weeks. Some tasks were originally run in parallel on
> multiple threads.

* **Hitmap computations** in particular were executed manually in parallel,
  which took around a week on a computing server. If you run these
  single-threaded, they may take significantly longer.
* The **min\_justified** experiments support multithreading directly via a
  command-line argument.

### Computing xJR Probability Experiments

Run the following script to recompute results from scratch:

```bash
./exp_code/compute_all_xjrprobs.sh
```

### Computing Hitmaps

Run the following script to recompute results from scratch:

```bash
./exp_code/compute_all_hitmaps.sh
```

### Computing Heatmaps

Run the following script to recompute results from scratch:

```bash
./exp_code/compute_all_heatmaps.sh
```

### Computing Average Minimum Justified Groups

Run the following script to recompute results from scratch:

```bash
./exp_code/compute_all_min_justifieds.sh
```

## License

This code is licensed under the MIT License.
© 2025 [Andrzej Kaczmarczyk](https://akaczmarczyk.com)
