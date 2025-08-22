# Document Analysis Report
**Source**: paper3
**Generated**: 2025-08-22 15:15:46
**Total Chapters**: 6

## Document Overview
- **Total Words**: 2,233
- **Total Characters**: 18,844
- **Average Words per Chapter**: 372

## Chapter Summaries

### Chapter 1
**1. Introduction**
*Chapter Key Terms*: uhecrs(5), mass(5), data(4), however(4), composition(4)
*Paragraph Analysis*:
1. **Paragraph 1**: 1. Introduction
Withmorethan20yearsofobservations,thePierreAugerObservatory(Auger)andTelescope
Array...
   *Keywords*: uhecrs(5), mass(5), data(4)
*Chapter Summary*:
1. Nevertheless, with sophisticated analyses techniques, the combination of
currentlyavailablearrivaldirections,energies,andmasscompositiondatacanbeusedtoconstrain
the properties of potential sources and...
2. Introduction
Withmorethan20yearsofobservations,thePierreAugerObservatory(Auger)andTelescope
Array Project (TA) have provided us with a wealth of data on ultra-high energy cosmic rays
(UHECRs), and wil...
3. However, the association of UHECRs with their potential sources remains a
challenge due to the limited statistics and the complex propagation effects in the intergalactic and
Galactic medium.

*Word Count*: 242 | *Type*: Numbered Title

---

### Chapter 2
**2. Model
As with our previous work, the model used in this work is based on a Bayesian hierarchical
framework, where we set priors on the source parameters, such as the luminosity and spectral
indices, as well as the mass fractions of UHECRs at the source. The inference is performed using**
*Chapter Key Terms*: model(3), work(2), bayesian(2), source(2), parameters(2)
*Paragraph Analysis*:
1. **Paragraph 1**: 2. Model
As with our previous work, the model used in this work is based on a Bayesian hierarchical
...
   *Keywords*: model(3), work(2), bayesian(2)
*Chapter Summary*:
1. Model
As with our previous work, the model used in this work is based on a Bayesian hierarchical
framework, where we set priors on the source parameters, such as the luminosity and spectral
indices, a...
2. The inference is performed using
the probabilistic programming language stan[8], which performs Markov Chain Monte Carlo
(MCMC) sampling through the Hamiltonian Monte Carlo (HMC) algorithm to directly...

*Word Count*: 81 | *Type*: Numbered Title

---

### Chapter 3
**2.1 Modelling UHECR Propagation with PriNCe
To describe the mass-dependent propagation effects, we use the nuclear propagation code**
*Chapter Key Terms*: source(11), mass(8), model(8), propagation(6), earth(6)
*Paragraph Analysis*:
1. **Paragraph 1**: 2.1 Modelling UHECR Propagation with PriNCe
To describe the mass-dependent propagation effects, we u...
   *Keywords*: source(11), mass(8), model(8)
*Chapter Summary*:
1. Thesequantitiesareobtained
by summing over all mass species at Earth:
3
A Bayesian Framework for UHECR Source Association and Parameter Inference Keito Watanabe
JEarth
𝑙𝑘=∑︁
𝑖𝑌Earth
𝑖𝑙𝑘,⟨ln𝐴⟩𝑙𝑘=Í
𝑖𝑌Ea...
2. Source model: While the same propagation model is used to describe the UHECRs emitted from
thesourceandfrombackgroundsources,wemodelthemseparately.
3. Given 𝑁𝑆sources,eachsource
(labelled as𝑘) with a given luminosity 𝐿𝑘at distance𝑑𝑘(flux𝐹𝑘∝𝐿𝑘/4𝜋𝑑2
𝑘) is treated as a point
source that emits UHECRs with a single injection mass composition 𝐴𝑆
𝑙isotropi...

*Word Count*: 454 | *Type*: Subsection

---

### Chapter 4
**2.2 Forward Modeling & Inference with stan**
*Chapter Key Terms*: 𝐸bin(8), energy(6), model(6), earth(6), systematic(6)
*Paragraph Analysis*:
1. **Paragraph 1**: 2.2 Forward Modeling & Inference with stan
Energy & Mass Model: The total UHECR energy spectrum at E...
   *Keywords*: 𝐸bin(8), energy(6), model(6)
*Chapter Summary*:
1. 2.2 Forward Modeling & Inference with stan
Energy & Mass Model: The total UHECR energy spectrum at Earth is obtained by summing
contributionsfromeachinjectedmassspecies 𝐴𝑆
𝑙andallsources,includingthed...
2. The mean and variance of ln𝐴at Earth are similarly computed by summing over the injected
mass species contributions, now weighting by the expected number fraction of events from each
source,𝑁ex
𝑘/𝑁ex
...
3. To account for these effects, we model the
detectorresponseforeachsampledenergy 𝐸,andforeachbinin ⟨ln𝐴⟩andVar(ln𝐴),astruncated
Gaussian distributions centered around the true values, including global ...

*Word Count*: 359 | *Type*: Subsection

---

### Chapter 5
**3. Results
To verify our model, we apply it to simulated datasets based on the detector configurations**
*Chapter Key Terms*: source(18), auger(11), inferred(10), truth(10), figure(9)
*Paragraph Analysis*:
1. **Paragraph 1**: 3. Results
To verify our model, we apply it to simulated datasets based on the detector configuratio...
   *Keywords*: source(18), auger(11), inferred(10)
*Chapter Summary*:
1. Nonetheless,thetrueparametervalues
5
A Bayesian Framework for UHECR Source Association and Parameter Inference Keito Watanabe
101610171018101910201021E2dN
dE / eVTA, Source H
He
NSi
FeT otal
Truth
19....
2. Thisverifiestheaccuratereconstructionofdetectedenergies
within 1𝜎confidence and the mass moments of ln𝐴within 3𝜎, reflecting the reduced binning
6
A Bayesian Framework for UHECR Source Association and...
3. Middle: Inferred energy spectrum, weighted
by the inferred flux contributions from the point and background sources.

*Word Count*: 671 | *Type*: Numbered Title

---

### Chapter 6
**4. Conclusion
In this work, we presented a Bayesian hierarchical framework that integrates individual event
energiesandstatisticallyaveraged,binnedmasscompositiondatatoinferthepropertiesofUHECR
sources, including luminosity, spectral indices, and injected mass fractions. The nuclear prop-**
*Chapter Key Terms*: auger(10), astrophys(10), collaboration(8), watanabe(7), pierre(6)
*Paragraph Analysis*:
1. **Paragraph 1**: 4. Conclusion
In this work, we presented a Bayesian hierarchical framework that integrates individua...
   *Keywords*: auger(10), astrophys(10), collaboration(8)
*Chapter Summary*:
1. [17] Pierre Auger collaboration, Astrophys.
2. [18] Telescope Array, Pierre Auger collaboration, PoSICRC2021 (2021) 337.
3. [16] Pierre Auger collaboration, Phys.

*Word Count*: 426 | *Type*: Numbered Title

---

## Full Content

### 1. Introduction

1. Introduction
Withmorethan20yearsofobservations,thePierreAugerObservatory(Auger)andTelescope
Array Project (TA) have provided us with a wealth of data on ultra-high energy cosmic rays
(UHECRs), and will provide us with even more data with the AugerPrime upgrade [1] and TAx4
experiment [2]. However, the association of UHECRs with their potential sources remains a
challenge due to the limited statistics and the complex propagation effects in the intergalactic and
Galactic medium. In particular, the mass composition of UHECRs has not been measured on
an event-by-event basis, but rather only as a statistical average of all observed UHECRs. This
limitstheconstraintsplacedontherigidity-dependentdeflectionsandmass-dependentpropagation
losses of each UHECR. Nevertheless, with sophisticated analyses techniques, the combination of
currentlyavailablearrivaldirections,energies,andmasscompositiondatacanbeusedtoconstrain
the properties of potential sources and the propagation effects of UHECRs [3].
Inpreviousworks,wedevelopedaBayesianhierarchicalmodelcapableofinferringultra-high-
energy cosmic ray (UHECR) source parameters, such as luminosity and spectral indices, while
accountingformass-dependentpropagationeffectsusingthenuclearpropagationcode PriNCe[4–
7]. However, earlier iterations of this model required assumptions about the arrival composition
falling within a predefined mass group, limiting its direct applicability to observational data. In
this work, we relax this assumption by explicitly incorporating the mean and variance of the
logarithmic mass ( ln𝐴) distribution measured at Earth. We demonstrate that combining these
mass composition moments with individual event energies is sufficient to robustly infer source
parameters, including the initial UHECR mass composition at the sources. We present detailed
analyses of simulated datasets reflecting the exposures of the Pierre Auger Observatory and the
Telescope Array, highlighting the method’s performance and applicability to currently available
observational data.

---

### 2. Model
As with our previous work, the model used in this work is based on a Bayesian hierarchical
framework, where we set priors on the source parameters, such as the luminosity and spectral
indices, as well as the mass fractions of UHECRs at the source. The inference is performed using

2. Model
As with our previous work, the model used in this work is based on a Bayesian hierarchical
framework, where we set priors on the source parameters, such as the luminosity and spectral
indices, as well as the mass fractions of UHECRs at the source. The inference is performed using
the probabilistic programming language stan[8], which performs Markov Chain Monte Carlo
(MCMC) sampling through the Hamiltonian Monte Carlo (HMC) algorithm to directly obtain the
posterior distributions of the model parameters.

---

### 2.1 Modelling UHECR Propagation with PriNCe
To describe the mass-dependent propagation effects, we use the nuclear propagation code

2.1 Modelling UHECR Propagation with PriNCe
To describe the mass-dependent propagation effects, we use the nuclear propagation code
PriNCe[7]. Thiscodedescribesitsnuclearpropagationasaseriesofpartialdifferentialequations
and numerically solves for the co-moving density of UHECRs 𝑌𝑖(𝐸𝑖,𝑧)=𝑁𝑖(𝐸𝑖,𝑧)/(1+𝑧)3for
each mass component 𝑖at a given energy 𝐸𝑖and redshift 𝑧. The propagation equation is given by:
𝜕𝑧𝑌𝑖(𝐸𝑖,𝑧)=−𝜕𝐸(𝑏ad𝑌𝑖)−𝜕𝐸(𝑏𝑒+𝑒−𝑌𝑖)−Γ𝑖𝑌𝑖+∑︁
𝑗𝑄𝑖→𝑗𝑌𝑗+𝐽𝑖, (1)
2
A Bayesian Framework for UHECR Source Association and Parameter Inference Keito Watanabe
which describes (in order from left to right) the adiabatic losses, pair production losses and photo-
nuclearinteractions(decayandre-injection). Thelastterm 𝐽𝑖=𝐽𝑖(𝐸𝑖,𝑧,𝐴𝑆
𝑖)describestheinjection
from a distribution of homogeneously distributed and isotropically emitting sources, where 𝐴𝑆
𝑖
denotesthemassnumberofcomponent 𝑖atthesource. Inthiswork,wedescribethephoto-nuclear
and photo-hadronic cross sections with TALYS[9] and SOPHIA[10] respectively.
Source model: While the same propagation model is used to describe the UHECRs emitted from
thesourceandfrombackgroundsources,wemodelthemseparately. Given 𝑁𝑆sources,eachsource
(labelled as𝑘) with a given luminosity 𝐿𝑘at distance𝑑𝑘(flux𝐹𝑘∝𝐿𝑘/4𝜋𝑑2
𝑘) is treated as a point
source that emits UHECRs with a single injection mass composition 𝐴𝑆
𝑙isotropically without any
backgroundsources. Thisamountstosetting 𝐽𝑖=0inEq.(1)andsettingtheinitialconditionofthe
co-moving density 𝑌𝑖at𝑧𝑘=𝑧(𝑑𝑘)with the energy distribution of UHECRs for a single injected
mass at the source (i.e. the source spectrum). The source spectrum follows that of [11]:
J𝑆
𝑙𝑘(𝐸𝑖,𝑍𝑆
𝑙|𝛼𝑘,𝑅max)∝𝐸𝑖
1 EeV−𝛼𝑘
× 
1 : 𝐸𝑖< 𝑍𝑆
𝑙𝑅max
exp 
1−𝐸𝑖
𝑍𝑆
𝑙𝑅max!
:𝐸𝑖≥𝑍𝑆
𝑙𝑅max(2)
where𝑍𝑆
𝑙denotes the charge number corresponding to the injected mass 𝐴𝑆
𝑙. Each source is
characterizedbyaspectralindex 𝛼𝑘andamaximalrigidity 𝑅max,whichisassumedtobeidentical
forallinjectedelements. Althoughpreviousstudieshaveindicatedthatmaximalrigiditymayvary
betweensourcesduetodifferencesintheiraccelerationproperties,wecurrentlyfix 𝑅max=1.7 EeV
for all sources following earlier analyses [7, 12]. The normalization constant, representing the
number of injected particles with mass 𝐴𝑆
𝑙per comoving volume, per unit energy, and per year, is
determined within the forward model implemented in stan.
Background Model: Our background model assumes the continuous injection of UHECRs from
sourceshomogeneouslydistributedfromredshift 𝑧max=3downtoatruncationredshift 𝑧trunc. This
is modeled by setting initial conditions 𝑌𝑖(𝐸𝑖,𝑧)=0and defining the injection function 𝐽𝑖𝑙as:
𝐽𝑖𝑙(𝐸𝑖,𝑧,𝑍𝑆
𝑙|𝛼0,𝑅max)= 
𝑛evol(𝑧)J𝑆
𝑙𝑘(𝐸𝑖,𝑍𝑆
𝑙|𝛼0,𝑅max), 𝑧≥𝑧trunc
0, 𝑧<𝑧 trunc.(3)
Analogous to the source model, the background model is described by a spectral index 𝛼0, a fixed
maximal rigidity 𝑅max=1.7 EeV, mass fractions 𝑓𝐴
𝑙0for each injected composition, and a total
normalization flux 𝐹0. We assume that the source density 𝑛evol(𝑧)evolves with redshift according
to the star formation rate (SFR) parameterization from Ref. [13].
UsingEqs.(2)to(3),wegenerateadatabaseofsolutionsbysolvingEq.(1)onagridofspectral
indices and injection masses. In our analysis, we consider 𝑁𝐴
inj=5injected mass groups: proton
(𝐴=1), helium (𝐴=4), nitrogen (𝐴=14), silicon (𝐴=28), and iron (𝐴=56). The resulting
comoving density at Earth, 𝑌Earth
𝑖𝑙𝑘:=𝑌𝑖(𝐸𝑖,𝑧=0,𝑍𝑆
𝑙|𝛼𝑘), is used to calculate the flux at Earth
JEarth
𝑙𝑘,aswellasthespectrum-weightedmeanandvarianceof ln𝐴. Thesequantitiesareobtained
by summing over all mass species at Earth:
3
A Bayesian Framework for UHECR Source Association and Parameter Inference Keito Watanabe
JEarth
𝑙𝑘=∑︁
𝑖𝑌Earth
𝑖𝑙𝑘,⟨ln𝐴⟩𝑙𝑘=Í
𝑖𝑌Earth
𝑖𝑙𝑘ln𝐴𝑖Í
𝑖𝑌Earth
𝑖𝑙𝑘,Var(ln𝐴)𝑙𝑘=Í
𝑖𝑌Earth
𝑖𝑙𝑘(ln𝐴𝑖)2
Í
𝑖𝑌Earth
𝑖𝑙𝑘−⟨ln𝐴⟩2
𝑙𝑘.
(4)
This precomputed database is then used in the implementation of the forward model in stanto
perform Bayesian inference.

---

### 2.2 Forward Modeling & Inference with stan

2.2 Forward Modeling & Inference with stan
Energy & Mass Model: The total UHECR energy spectrum at Earth is obtained by summing
contributionsfromeachinjectedmassspecies 𝐴𝑆
𝑙andallsources,includingthediffusebackground:
J(𝐸)=𝑁𝑆∑︁
𝑘=0𝑁𝐴
inj∑︁
𝑙=1𝑓𝐴
𝑙𝑘𝐹𝑘JEarth
𝑙𝑘(𝐸)=𝑁𝑆∑︁
𝑘=0𝑁𝐴
inj∑︁
𝑙=1𝑓𝐴
𝑙𝑘𝑓𝐹
𝑘𝐹totJEarth
𝑙𝑘(𝐸), (5)
where the expected number of detected events 𝑁ex
𝑘for each source is determined by weighting
the detector exposure 𝜖𝑇with the integrated energy spectrum. Here, the spectrum at Earth is
weighted by the source- and composition-dependent mass fractions 𝑓𝐴
𝑙𝑘and the source-dependent
flux fractions 𝑓𝐹
𝑘, multiplied by the total flux 𝐹tot. These weighted spectra are used to sample
individual UHECR energies 𝐸Earthin our inference procedure.
The mean and variance of ln𝐴at Earth are similarly computed by summing over the injected
mass species contributions, now weighting by the expected number fraction of events from each
source,𝑁ex
𝑘/𝑁ex
tot, instead of the flux:
⟨ln𝐴⟩(𝐸bin)=𝑁𝑆∑︁
𝑘=0𝑁𝐴
inj∑︁
𝑙=1𝑓𝐴
𝑙𝑘𝑁ex
𝑘
𝑁ex
tot⟨ln𝐴⟩𝑙𝑘,Var(ln𝐴)(𝐸bin)=𝑁𝑆∑︁
𝑘=0𝑁𝐴
inj∑︁
𝑙=1𝑓𝐴
𝑙𝑘𝑁ex
𝑘
𝑁ex
totVar(ln𝐴)𝑙𝑘.(6)
Sinceevent-by-eventcompositioninformationiscurrentlyunavailable,weadoptabinnedapproach,
samplingthemeanandvarianceof ln𝐴withindiscreteenergybins 𝐸binseparatefromtheindivid-
ually sampled energies in Eq. (5). Thus, mass composition measurements act as global external
constraints within our Bayesian inference framework.
Detector Model: UHECRmeasurementsatobservatorieslikeAugerorTAareinfluencedbyboth
statistical fluctuations and systematic uncertainties arising from calibration effects and hadronic
model dependencies in the reconstruction process. To account for these effects, we model the
detectorresponseforeachsampledenergy 𝐸,andforeachbinin ⟨ln𝐴⟩andVar(ln𝐴),astruncated
Gaussian distributions centered around the true values, including global systematic shifts:
𝐸det∼TruncatedLogNormal (log𝐸+𝜈log𝐸, 𝜎log𝐸, 𝐸th, 𝐸max), (7)
⟨ln𝐴⟩det(𝐸bin)∼TruncatedNormal(⟨ln𝐴⟩(𝐸bin)+𝜈𝜇ln𝐴, 𝜎𝜇ln𝐴(𝐸bin),0,∞), (8)
Var(ln𝐴)det(𝐸bin)∼TruncatedNormal(Var(ln𝐴)(𝐸bin)+𝜈Var ln𝐴, 𝜎Var ln𝐴(𝐸bin),−1,∞),(9)
where𝜈log𝐸,𝜈𝜇ln𝐴, and𝜈Var ln𝐴represent systematic uncertainties in the reconstructed energy,
mean ln𝐴, and variance of ln𝐴, respectively. The corresponding statistical uncertainties, denoted
by𝜎log𝐸,𝜎𝜇ln𝐴, and𝜎Var ln𝐴, are allowed to vary within each energy bin. The truncation ensures
4
A Bayesian Framework for UHECR Source Association and Parameter Inference Keito Watanabe
physically meaningful results. Specifically, for the variance, a lower truncation bound of −1is
chosen to account for systematic shifts potentially leading to negative observed variance values.
Prior Model: We specify weakly informative priors for the model parameters as follows:
𝛼𝑘∼N(− 1,3), 𝑓𝐴
𝑘∼Dir(Vec(1, 𝑁𝐴
inj)), 𝑓𝐹∼Dir(Vec(1, 𝑁𝑆+1)),log10𝐹tot∼N(− 1,3),
(10)
where Dirichlet priors ensure that both the mass fractions 𝑓𝐴
𝑘and flux fractions 𝑓𝐹sum to unity.
Systematic uncertainties are assigned weakly informative priors: 𝜈log𝐸∼N( 0,0.1),𝜈𝜇ln𝐴∼
N(0,1), and𝜈Var ln𝐴∼N( 0,1).

---

### 3. Results
To verify our model, we apply it to simulated datasets based on the detector configurations

3. Results
To verify our model, we apply it to simulated datasets based on the detector configurations
of Auger and TA. We assume a single point source (now labeled SRC) located at 𝑑=4 Mpc,
motivated by potential source candidates (Centaurus A, M82) for both hemispheres at similar
distances[14,15]. Thecontinuousinjectionfrombackgroundsources(labeledBG)isalsotruncated
at the same distance. We set identical source parameters for both detectors, specifically choosing:
𝛼SRC=−0.5,𝛼BG=0.5,𝐿SRC=7×1041erg s−1,𝑓𝐴
SRC=(0,0.35,0.5,0.1,0.05), and𝑓𝐴
BG=
(0,0.2,0.4,0.3,0.1). The source association fraction is set to 𝑓assos=Í𝑁𝑆
𝑘=1𝑁ex
𝑘/𝑁ex
tot=0.1,
defining the relative contribution of the point source(s) to the overall observed data. Simulated
datasets are generated using Eq. (5) to sample energies 𝐸Earthfor each UHECR, and Eq. (6) to
samplethemeanandvarianceof ln𝐴,utilizingenergybinsfrom[16]. Detectorresponsesarethen
applied to emulate observed energies and mass compositions, which we subsequently use in our
inference model to reconstruct source parameters.
Detector𝑁ev𝜖𝑇/km2yr sr𝜎log𝐸𝜎𝜇ln𝐴𝜎Var ln𝐴𝜈log𝐸𝜈𝜇ln𝐴𝜈Var ln𝐴
TA680 30500 0.20.2 0.2-0.05 0.3 0.5
Auger 2750 122000 0.10.1 0.10.050.3 0.5
Table 1: Detector parameters used in this work. Statistical uncertainties reflect differences in detector
exposure𝜖𝑇, as indicated by the number of events 𝑁ev. Systematic uncertainties are motivated by the
energyrescalingfromthejointAuger-TAenergyspectrumworkinggroupandupperlimitsfromcurrent ln𝐴
measurements.
Table1summarizesthestatisticalandsystematicparametersforeachdetectormodel. Toensure
comparability,weusethedetectorexposurefromtheAugerPhaseOnedataset[17],andtake1/4of
thistotalexposureforthedetectorexposureofTA.Correspondingly,statisticaluncertaintiesforTA
are doubled. Systematic uncertainties are derived from energy rescaling efforts by the Auger-TA
energy spectrum working group [18] and upper limits from [16].
Figure 1 presents reconstruction results from simulated TA and Auger datasets. The inferred
sourcespectraandspectrum-weightedmassfractionsofeachsourcecomponentarerecoveredwell,
demonstrating accurate propagation of information through the model. The reconstructed energy
spectraandmasscompositionmomentsforbothdetectorsalignwellwithtruevalues,althoughthe
TAresultsexhibitlargeruncertaintiesduetolowerexposure. Nonetheless,thetrueparametervalues
5
A Bayesian Framework for UHECR Source Association and Parameter Inference Keito Watanabe
101610171018101910201021E2dN
dE / eVTA, Source H
He
NSi
FeT otal
Truth
19.6 19.8 20.0 20.2 20.4
log10(E/eV)0.000.250.500.751.00fA
101610171018101910201021E2dN
dE / eVAuger, Source H
He
NSi
FeT otal
Truth
19.6 19.8 20.0 20.2 20.4
log10(E/eV)0.000.250.500.751.00fA
19.6 19.8 20.0 20.2 20.4
log10(E/eV)1035103610371038E3J(E) / eV2km2yr1sr1
TA Source
Background
T otal
Truth
18.6 18.8 19.0 19.2 19.4 19.6 19.8 20.0
log10(Ebin/eV)024lnA
18.6 18.8 19.0 19.2 19.4 19.6 19.8 20.0
log10(Ebin/eV)01Var(lnA)
19.6 19.8 20.0 20.2 20.4
log10(E/eV)1035103610371038E3J(E) / eV2km2yr1sr1
Auger Source
Background
T otal
Truth
18.6 18.8 19.0 19.2 19.4 19.6 19.8 20.0
log10(Ebin/eV)024lnA
18.6 18.8 19.0 19.2 19.4 19.6 19.8 20.0
log10(Ebin/eV)01Var(lnA)
19.6 19.7 19.8 19.9 20.0 20.1 20.2 20.3
log10(Edet/eV)100101102103Counts per binTA PPC
PPCs : Mean
Truth
18.6 18.8 19.0 19.2 19.4 19.6 19.8 20.0
log10(Ebin/eV)024lnAdet
18.6 18.8 19.0 19.2 19.4 19.6 19.8 20.0
log10(Ebin/eV)02Var(lnA)det
19.6 19.7 19.8 19.9 20.0 20.1 20.2 20.3
log10(Edet/eV)100101102103Counts per binAuger PPC
PPCs : Mean
Truth
18.6 18.8 19.0 19.2 19.4 19.6 19.8 20.0
log10(Ebin/eV)024lnAdet
18.6 18.8 19.0 19.2 19.4 19.6 19.8 20.0
log10(Ebin/eV)02Var(lnA)det
Figure 1: ReconstructedresultsfromsimulateddatasetsbasedonTA(left)andAuger(right). Top: Inferred
source spectrum of the point source, weighted by inferred mass fractions for each injected composition.
Insets show spectrum-weighted mass fractions at each energy. Middle: Inferred energy spectrum, weighted
by the inferred flux contributions from the point and background sources. Insets display mean and variance
ofln𝐴perenergybin. Bottom: Posteriorpredictivechecks(PPCs),demonstratingforward-modeledresults.
Shaded regions represent the 1, 2, and 3 𝜎confidence intervals around the mean (black solid lines). True
values are indicated by dashed lines.
consistently lie within the inferred 2 𝜎uncertainty intervals for all inferred source parameters, as
shown in Figure 2.
Wealsoperformposteriorpredictivechecks(PPCs)bygeneratingrealizationsofthesimulated
datasetsusing100posteriorsamples. Thisverifiestheaccuratereconstructionofdetectedenergies
within 1𝜎confidence and the mass moments of ln𝐴within 3𝜎, reflecting the reduced binning
6
A Bayesian Framework for UHECR Source Association and Parameter Inference Keito Watanabe
0.20.40.60.81.0BG
3839404142log10(LSRC/ergs1)
0.10.20.30.40.5fp,SRC
0.20.40.60.81.0fN,SRC
0.10.20.30.40.5fFe,SRC
0.10.20.30.40.5fp,BG
0.20.40.60.81.0fN,BG
0.10.20.30.40.5fFe,BG
1.5
0.01.53.0
SRC
1.6
1.2
0.8
0.4
0.0log10(fassos)
0.20.40.60.81.0
BG
3839404142
log10(LSRC/ergs1)
0.10.20.30.40.5
fp,SRC0.20.40.60.81.0
fN,SRC0.10.20.30.40.5
fFe,SRC0.10.20.30.40.5
fp,BG0.20.40.60.81.0
fN,BG0.10.20.30.40.5
fFe,BG1.6
1.2
0.8
0.4
0.0
log10(fassos)TA
Auger
Figure 2: Cornerplotofjointposteriordistributionsforkeysourceparameters: spectralindicesforpointand
background sources, source luminosity, proton, nitrogen, and iron mass fractions for point and background
sources, and source association fraction. Results from TA (blue) and Auger (red) are shown, with contours
representing 1, 2, and 3 𝜎intervals. True simulation values are indicated by black lines and dots. Figure
generated using corner.py [19].
resolution employed in the current model. We also note that the inferred parameter contours in
Figure2arenotexclusivelydominatedbystatisticaluncertainty;rather,theyreflectlimitationsdue
to insufficiently detailed features in the spectral and average composition data alone. Therefore,
incorporating spatial information and, ultimately, event-by-event mass measurements is expected
to significantly improve constraints on source parameters.

---

### 4. Conclusion
In this work, we presented a Bayesian hierarchical framework that integrates individual event
energiesandstatisticallyaveraged,binnedmasscompositiondatatoinferthepropertiesofUHECR
sources, including luminosity, spectral indices, and injected mass fractions. The nuclear prop-

4. Conclusion
In this work, we presented a Bayesian hierarchical framework that integrates individual event
energiesandstatisticallyaveraged,binnedmasscompositiondatatoinferthepropertiesofUHECR
sources, including luminosity, spectral indices, and injected mass fractions. The nuclear prop-
7
A Bayesian Framework for UHECR Source Association and Parameter Inference Keito Watanabe
agation code PriNCeis employed to model the observed energy spectrum and the mean and
variance of ln𝐴at Earth, clearly distinguishing between discrete injections from point sources
and continuous injections from a homogeneous background. Our forward model also accounts for
detectorresponses,incorporatingbothstatisticalandsystematicuncertainties. Throughapplication
to simulated datasets representative of the Auger and TA observatories, we demonstrated that our
framework reliably reconstructs the true source parameters at each stage of the modeling process.
Previously,weshowedthatrigidity-dependentdeflectionsfromGalacticandextragalacticmag-
netic fields can be incorporated alongside energy and mass composition models [4–6]. Our future
plansinvolveintegratingthisdeflectionmodelintothecurrentframework,enablingacomprehensive
analysis that utilizes all available observational information from existing UHECR observatories.
We aim to apply this extended approach to publicly available data from Auger and TA, eventually
expanding the analysis to include catalogs of potential point-source candidates such as starburst
galaxies.
Acknowledgements We acknowledge support from Academia Sinica under Grant No. AS-GCS-113-
M04. AF acknowledges additional support from the National Science and Technology Council under Grant
No. 113-2112-M-001-060-MY3. Computational resources were provided by the Academia Sinica Grid
Computing Center (ASGC) with support from the Institute of Physics, Academia Sinica.
References
[1]Pierre Auger collaboration, EPJ Web Conf. 210(2019) 06002 [ 1905.04472 ].
[2]Telescope Array collaboration, Nucl. Instrum. Meth. A 1019(2021) 165726 [ 2103.01086 ].
[3]Pierre Auger collaboration, JCAP 01(2024) 022 [ 2305.16693 ].
[4] K. Watanabe et al., EPJ Web Conf. 283(2023) 03009.
[5] K. Watanabe et al., PoSICRC2023 (2023) 479.
[6] K. Watanabe et al., PoSUHECR2024 (2025) 017.
[7] J. Heinze et al., Astrophys. J. 873(2019) 88 [ 1901.03338 ].
[8] S.D. Team, Stan modeling language users guide and reference manual , 2024.
[9] A.J. Koning et al., AIP Conf. Proc. 769(2005) 1154.
[10] A. Mucke et al., Comput. Phys. Commun. 124(2000) 290 [ astro-ph/9903478 ].
[11] Pierre Auger collaboration, JCAP 04(2017) 038 [ 1612.07155 ].
[12] D. Ehlert et al., Phys. Rev. D 107(2023) 103045 [ 2207.10691 ].
[13] H. Yüksel et al., Astrophys. J. Lett. 683(2008) L5 [ 0804.4008 ].
[14] Telescope Array collaboration, Astrophys. J. Lett. 867(2018) L27 [ 1809.01573 ].
[15] H. Yüksel et al., Astrophys. J. 758(2012) 16 [ 1203.3197 ].
[16] Pierre Auger collaboration, Phys. Rev. D 111(2025) 022003 [ 2406.06319 ].
[17] Pierre Auger collaboration, Astrophys. J. 935(2022) 170 [ 2206.13492 ].
[18] Telescope Array, Pierre Auger collaboration, PoSICRC2021 (2021) 337.
[19] D. Foreman-Mackey, The Journal of Open Source Software 1(2016) 24.
8

---
