# Paper Text Segmentation Report: paper3.pdf

## Document Statistics
- **File:** `paper3.pdf`
- **Total Sections:** 8
- **Total Paragraphs:** 68

## Section Overview
| Section | Paragraphs |
|---------|------------|
| Keito Watanabe 𝑎 Anatoli | 10 |
| 1 Introduction | 2 |
| 2 Model | 1 |
| 21 Modelling Uhecr Propagation | 10 |
| 22 Forward Modeling Inference | 10 |
| 3 Results | 11 |
| 4 Conclusion | 5 |
| References | 19 |

## Paper Content by Sections

### Keito Watanabe 𝑎 Anatoli

**1.** 𝑎 Institute for Astroparticle Physics, Karlsruhe Institute of Technology, Hermann-von-Helmholtz-Platz 1, 76344 Eggenstein-Leopoldshafen, Germany

**2.** 𝑏 Institute of Physics, Academia Sinica, No. 128, Sec. 2, Academia Rd, Nangang District, 11529 Taipei, Taiwan

**3.** 𝑐 Max Planck Institute for Physics, Boltmannstr. 8, Garching 85748, Germany

**4.** 𝑑 Institute for Cosmic Ray Research, the University of Tokyo, 5-1-5 Kashiwa-no-ha, Kashiwa, Chiba 277-8582, Japan

**5.** E-mail: keito.watanabe@kit.edu, anatoli@gate.sinica.edu.tw,

**6.** capel@mpp.mpg.de, hsagawa@icrr.u-tokyo.ac.jp

**7.** The identification of potential sources of ultra-high-energy cosmic rays (UHECRs) remains challenging due to magnetic deflections and propagation losses, which are particularly strong for nuclei. In previous iterations of this work, we proposed an approach for UHECR astronomy based on Bayesian inference through explicit modelling of propagation and magnetic deflection effects. The event-by-event mass information is expected to provide tighter constraints on these parameters and to help identify unknown sources. However, the measurements of the average mass through observations from the surface detectors at the Pierre Auger Observatory already indicate that the UHECR masses are well represented through its statistical average. In this contribution, we present our framework which uses energy and mass moments of ln 𝐴 to infer the source parameters of UHECRs, including the mass composition at the source. We demonstrate the performance of our model using simulated datasets based on the Pierre Auger Observatory and Telescope Array Project. Our model can be readily applied to currently available data, and we discuss the implications of our results for UHECR source identification.

**8.** 39th International Cosmic Ray Conference (ICRC2025) 15-24 July 2025 Geneva, Switzerland

**9.** © Copyright owned by the author(s) under the terms of the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License (CC BY-NC-ND 4.0).

**10.** A Bayesian Framework for UHECR Source Association and Parameter Inference

---

### 1 Introduction

**1.** With more than 20 years of observations, the Pierre Auger Observatory (Auger) and Telescope Array Project (TA) have provided us with a wealth of data on ultra-high energy cosmic rays (UHECRs), and will provide us with even more data with the AugerPrime upgrade [1] and TAx4 experiment [2]. However, the association of UHECRs with their potential sources remains a challenge due to the limited statistics and the complex propagation effects in the intergalactic and Galactic medium. In particular, the mass composition of UHECRs has not been measured on an event-by-event basis, but rather only as a statistical average of all observed UHECRs. This limits the constraints placed on the rigidity-dependent deflections and mass-dependent propagation losses of each UHECR. Nevertheless, with sophisticated analyses techniques, the combination of currently available arrival directions, energies, and mass composition data can be used to constrain the properties of potential sources and the propagation effects of UHECRs [3].

**2.** In previous works, we developed a Bayesian hierarchical model capable of inferring ultra-highenergy cosmic ray (UHECR) source parameters, such as luminosity and spectral indices, while accounting for mass-dependent propagation effects using the nuclear propagation code PriNCe [47]. However, earlier iterations of this model required assumptions about the arrival composition falling within a predefined mass group, limiting its direct applicability to observational data. In this work, we relax this assumption by explicitly incorporating the mean and variance of the logarithmic mass (ln 𝐴 ) distribution measured at Earth. We demonstrate that combining these mass composition moments with individual event energies is sufficient to robustly infer source parameters, including the initial UHECR mass composition at the sources. We present detailed analyses of simulated datasets reflecting the exposures of the Pierre Auger Observatory and the Telescope Array, highlighting the method's performance and applicability to currently available observational data.

---

### 2 Model

**1.** As with our previous work, the model used in this work is based on a Bayesian hierarchical framework, where we set priors on the source parameters, such as the luminosity and spectral indices, as well as the mass fractions of UHECRs at the source. The inference is performed using the probabilistic programming language stan [8], which performs Markov Chain Monte Carlo (MCMC) sampling through the Hamiltonian Monte Carlo (HMC) algorithm to directly obtain the posterior distributions of the model parameters.

---

### 21 Modelling Uhecr Propagation

**1.** To describe the mass-dependent propagation effects, we use the nuclear propagation code PriNCe [7]. This code describes its nuclear propagation as a series of partial differential equations and numerically solves for the co-moving density of UHECRs 𝑌 𝑖 ( 𝐸 𝑖 , 𝑧 ) = 𝑁 𝑖 ( 𝐸 𝑖 , 𝑧 )/( 1 + 𝑧 ) 3 for each mass component 𝑖 at a given energy 𝐸 𝑖 and redshift 𝑧 . The propagation equation is given by:

**2.** A Bayesian Framework for UHECR Source Association and Parameter Inference

**3.** which describes (in order from left to right) the adiabatic losses, pair production losses and photonuclear interactions (decay and re-injection). The last term 𝐽 𝑖 = 𝐽 𝑖 ( 𝐸 𝑖 , 𝑧, 𝐴 𝑆 𝑖 ) describes the injection from a distribution of homogeneously distributed and isotropically emitting sources, where 𝐴 𝑆 𝑖 denotes the mass number of component 𝑖 at the source. In this work, we describe the photo-nuclear and photo-hadronic cross sections with TALYS [9] and SOPHIA [10] respectively.

**4.** Source model: While the same propagation model is used to describe the UHECRs emitted from the source and from background sources, we model them separately. Given 𝑁 𝑆 sources, each source (labelled as 𝑘 ) with a given luminosity 𝐿 𝑘 at distance 𝑑 𝑘 (flux 𝐹 𝑘 ∝ 𝐿 𝑘 / 4 𝜋𝑑 2 𝑘 ) is treated as a point source that emits UHECRs with a single injection mass composition 𝐴 𝑆 𝑙 isotropically without any background sources. This amounts to setting 𝐽 𝑖 = 0 in Eq. (1) and setting the initial condition of the co-moving density 𝑌 𝑖 at 𝑧 𝑘 = 𝑧 ( 𝑑 𝑘 ) with the energy distribution of UHECRs for a single injected mass at the source (i.e. the source spectrum). The source spectrum follows that of [11]:

**5.** where 𝑍 𝑆 𝑙 denotes the charge number corresponding to the injected mass 𝐴 𝑆 𝑙 . Each source is characterized by a spectral index 𝛼 𝑘 and a maximal rigidity 𝑅 max , which is assumed to be identical for all injected elements. Although previous studies have indicated that maximal rigidity may vary between sources due to differences in their acceleration properties, we currently fix 𝑅 max = 1 . 7 EeV for all sources following earlier analyses [7, 12]. The normalization constant, representing the number of injected particles with mass 𝐴 𝑆 𝑙 per comoving volume, per unit energy, and per year, is determined within the forward model implemented in stan .

**6.** Background Model: Our background model assumes the continuous injection of UHECRs from sources homogeneously distributed from redshift 𝑧 max = 3 down to a truncation redshift 𝑧 trunc . This is modeled by setting initial conditions 𝑌 𝑖 ( 𝐸 𝑖 , 𝑧 ) = 0 and defining the injection function 𝐽 𝑖𝑙 as:

**7.** Analogous to the source model, the background model is described by a spectral index 𝛼 0 , a fixed maximal rigidity 𝑅 max = 1 . 7 EeV, mass fractions 𝑓 𝐴 𝑙 0 for each injected composition, and a total normalization flux 𝐹 0 . We assume that the source density 𝑛 evol ( 𝑧 ) evolves with redshift according to the star formation rate (SFR) parameterization from Ref. [13].

**8.** Using Eqs. (2) to (3), we generate a database of solutions by solving Eq. (1) on a grid of spectral indices and injection masses. In our analysis, we consider 𝑁 𝐴 inj = 5 injected mass groups: proton ( 𝐴 = 1), helium ( 𝐴 = 4), nitrogen ( 𝐴 = 14), silicon ( 𝐴 = 28), and iron ( 𝐴 = 56). The resulting comoving density at Earth, 𝑌 Earth 𝑖𝑙𝑘 : = 𝑌 𝑖 ( 𝐸 𝑖 , 𝑧 = 0 , 𝑍 𝑆 𝑙 | 𝛼 𝑘 ) , is used to calculate the flux at Earth J Earth 𝑙𝑘 , as well as the spectrum-weighted mean and variance of ln 𝐴 . These quantities are obtained by summing over all mass species at Earth:

**9.** A Bayesian Framework for UHECR Source Association and Parameter Inference

**10.** This precomputed database is then used in the implementation of the forward model in stan to perform Bayesian inference.

---

### 22 Forward Modeling Inference

**1.** Energy & Mass Model: The total UHECR energy spectrum at Earth is obtained by summing contributions from each injected mass species 𝐴 𝑆 𝑙 and all sources, including the diffuse background:

**2.** where the expected number of detected events 𝑁 ex 𝑘 for each source is determined by weighting the detector exposure 𝜖 𝑇 with the integrated energy spectrum. Here, the spectrum at Earth is weighted by the source- and composition-dependent mass fractions 𝑓 𝐴 𝑙𝑘 and the source-dependent flux fractions 𝑓 𝐹 𝑘 , multiplied by the total flux 𝐹 tot . These weighted spectra are used to sample individual UHECR energies 𝐸 Earth in our inference procedure.

**3.** The mean and variance of ln 𝐴 at Earth are similarly computed by summing over the injected mass species contributions, now weighting by the expected number fraction of events from each source, 𝑁 ex 𝑘 / 𝑁 ex tot , instead of the flux:

**4.** Since event-by-event composition information is currently unavailable, we adopt a binned approach, sampling the mean and variance of ln 𝐴 within discrete energy bins 𝐸 bin separate from the individually sampled energies in Eq. (5). Thus, mass composition measurements act as global external constraints within our Bayesian inference framework.

**5.** Detector Model: UHECRmeasurements at observatories like Auger or TA are influenced by both statistical fluctuations and systematic uncertainties arising from calibration effects and hadronic model dependencies in the reconstruction process. To account for these effects, we model the detector response for each sampled energy 𝐸 , and for each bin in ⟨ ln 𝐴 ⟩ and Var ( ln 𝐴 ) , as truncated Gaussian distributions centered around the true values, including global systematic shifts:

**6.** where 𝜈 log 𝐸 , 𝜈 𝜇 ln 𝐴 , and 𝜈 Var ln 𝐴 represent systematic uncertainties in the reconstructed energy, mean ln 𝐴 , and variance of ln 𝐴 , respectively. The corresponding statistical uncertainties, denoted by 𝜎 log 𝐸 , 𝜎 𝜇 ln 𝐴 , and 𝜎 Var ln 𝐴 , are allowed to vary within each energy bin. The truncation ensures

**7.** A Bayesian Framework for UHECR Source Association and Parameter Inference

**8.** physically meaningful results. Specifically, for the variance, a lower truncation bound of -1 is chosen to account for systematic shifts potentially leading to negative observed variance values.

**9.** Prior Model: We specify weakly informative priors for the model parameters as follows:

**10.** where Dirichlet priors ensure that both the mass fractions 𝑓 𝐴 𝑘 and flux fractions 𝑓 𝐹 sum to unity. Systematic uncertainties are assigned weakly informative priors: 𝜈 log 𝐸 ∼ N( 0 , 0 . 1 ) , 𝜈 𝜇 ln 𝐴 ∼ N( 0 , 1 ) , and 𝜈 Var ln 𝐴 ∼ N( 0 , 1 ) .

---

### 3 Results

**1.** To verify our model, we apply it to simulated datasets based on the detector configurations of Auger and TA. We assume a single point source (now labeled SRC) located at 𝑑 = 4 Mpc, motivated by potential source candidates (Centaurus A, M82) for both hemispheres at similar distances [14, 15]. The continuous injection from background sources (labeled BG) is also truncated at the same distance. We set identical source parameters for both detectors, specifically choosing: 𝛼 SRC = -0 . 5, 𝛼 BG = 0 . 5, 𝐿 SRC = 7 × 10 41 erg s -1 , 𝑓 𝐴 SRC = ( 0 , 0 . 35 , 0 . 5 , 0 . 1 , 0 . 05 ) , and 𝑓 𝐴 BG = ( 0 , 0 . 2 , 0 . 4 , 0 . 3 , 0 . 1 ) . The source association fraction is set to 𝑓 assos = ˝ 𝑁 𝑆 𝑘 = 1 𝑁 ex 𝑘 / 𝑁 ex tot = 0 . 1, defining the relative contribution of the point source(s) to the overall observed data. Simulated datasets are generated using Eq. (5) to sample energies 𝐸 Earth for each UHECR, and Eq. (6) to sample the mean and variance of ln 𝐴 , utilizing energy bins from [16]. Detector responses are then applied to emulate observed energies and mass compositions, which we subsequently use in our inference model to reconstruct source parameters.

**2.** *[Table description: Table 1: Detector parameters used in this work. Statistical uncertainties reflect differences in det...]*

**3.** *[Table description: Table 1 summarizes the statistical and systematic parameters for each detector model. To ensure comp...]*

**4.** *[Figure description: Figure 1 presents reconstruction results from simulated TA and Auger datasets. The inferred source s...]*

**5.** A Bayesian Framework for UHECR Source Association and Parameter Inference

**6.** *[Figure description: Figure 1: Reconstructed results from simulated datasets based on TA (left) and Auger (right). Top : ...]*

**7.** consistently lie within the inferred 2 𝜎 uncertainty intervals for all inferred source parameters, as shown in Figure 2.

**8.** Wealso perform posterior predictive checks (PPCs) by generating realizations of the simulated datasets using 100 posterior samples. This verifies the accurate reconstruction of detected energies within 1 𝜎 confidence and the mass moments of ln 𝐴 within 3 𝜎 , reflecting the reduced binning

**9.** A Bayesian Framework for UHECR Source Association and Parameter Inference

**10.** *[Figure description: Figure 2: Corner plot of joint posterior distributions for key source parameters: spectral indices f...]*

**11.** resolution employed in the current model. We also note that the inferred parameter contours in Figure 2 are not exclusively dominated by statistical uncertainty; rather, they reflect limitations due to insufficiently detailed features in the spectral and average composition data alone. Therefore, incorporating spatial information and, ultimately, event-by-event mass measurements is expected to significantly improve constraints on source parameters.

---

### 4 Conclusion

**1.** In this work, we presented a Bayesian hierarchical framework that integrates individual event energies and statistically averaged, binned mass composition data to infer the properties of UHECR sources, including luminosity, spectral indices, and injected mass fractions. The nuclear prop-

**2.** A Bayesian Framework for UHECR Source Association and Parameter Inference

**3.** agation code PriNCe is employed to model the observed energy spectrum and the mean and variance of ln 𝐴 at Earth, clearly distinguishing between discrete injections from point sources and continuous injections from a homogeneous background. Our forward model also accounts for detector responses, incorporating both statistical and systematic uncertainties. Through application to simulated datasets representative of the Auger and TA observatories, we demonstrated that our framework reliably reconstructs the true source parameters at each stage of the modeling process.

**4.** Previously, we showed that rigidity-dependent deflections from Galactic and extragalactic magnetic fields can be incorporated alongside energy and mass composition models [4-6]. Our future plans involve integrating this deflection model into the current framework, enabling a comprehensive analysis that utilizes all available observational information from existing UHECR observatories. We aim to apply this extended approach to publicly available data from Auger and TA, eventually expanding the analysis to include catalogs of potential point-source candidates such as starburst galaxies.

**5.** Acknowledgements We acknowledge support from Academia Sinica under Grant No. AS-GCS-113M04. AF acknowledges additional support from the National Science and Technology Council under Grant No. 113-2112-M-001-060-MY3. Computational resources were provided by the Academia Sinica Grid Computing Center (ASGC) with support from the Institute of Physics, Academia Sinica.

---

### References

**1.** Pierre Auger collaboration, EPJ Web Conf. 210 (2019) 06002 [ 1905.04472 ].

**2.** Telescope Array collaboration, Nucl. Instrum. Meth. A 1019 (2021) 165726 [ 2103.01086 ].

**3.** Pierre Auger collaboration, JCAP 01 (2024) 022 [ 2305.16693 ].

**4.** K. Watanabe et al., EPJ Web Conf. 283 (2023) 03009.

**5.** K. Watanabe et al., PoS ICRC2023 (2023) 479.

**6.** K. Watanabe et al., PoS UHECR2024 (2025) 017.

**7.** J. Heinze et al., Astrophys. J. 873 (2019) 88 [ 1901.03338 ].

**8.** S.D. Team, Stan modeling language users guide and reference manual , 2024.

**9.** A.J. Koning et al., AIP Conf. Proc. 769 (2005) 1154.

**10.** A. Mucke et al., Comput. Phys. Commun. 124 (2000) 290 [ astro-ph/9903478 ].

**11.** Pierre Auger collaboration, JCAP 04 (2017) 038 [ 1612.07155 ].

**12.** D. Ehlert et al., Phys. Rev. D 107 (2023) 103045 [ 2207.10691 ].

**13.** H. Yüksel et al., Astrophys. J. Lett. 683 (2008) L5 [ 0804.4008 ].

**14.** Telescope Array collaboration, Astrophys. J. Lett. 867 (2018) L27 [ 1809.01573 ].

**15.** H. Yüksel et al., Astrophys. J. 758 (2012) 16 [ 1203.3197 ].

**16.** Pierre Auger collaboration, Phys. Rev. D 111 (2025) 022003 [ 2406.06319 ].

**17.** Pierre Auger collaboration, Astrophys. J. 935 (2022) 170 [ 2206.13492 ].

**18.** Telescope Array, Pierre Auger collaboration, PoS ICRC2021 (2021) 337.

**19.** D. Foreman-Mackey, The Journal of Open Source Software 1 (2016) 24.

---

## Processing Details

### Method
- **Tool:** Docling Document Converter
- **Section Detection:** SectionHeaderItem identification + content pattern matching
- **Paragraph Extraction:** Content filtering with reference summarization
- **Structure:** Genuine section headers only, with paragraph-level content organization

### Notes
- References are summarized rather than listed in full detail
- Figure and table descriptions are preserved but condensed
- Author affiliations are summarized when extensive
- Only genuine section headers are used for document structure

