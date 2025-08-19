# Chromo: A High-Performance Python Interface to Hadronic Event Generators for Collider and Cosmic-Ray Simulations

###### Abstract

Simulations of hadronic and nuclear interactions are essential in both collider and astroparticle physics. The Chromo package provides a unified Python interface to multiple widely used hadronic event generators, including EPOS, DPMJet, Sibyll, QGSJet, and Pythia. Built on top of their original Fortran and C++ implementations, Chromo offers a zero-overhead abstraction layer suitable for use in Python scripts, Jupyter notebooks, or from the command line, while preserving the performance of direct calls to the generators. It is easy to install via precompiled binary wheels distributed through PyPI, and it integrates well with the Scientific Python ecosystem. Chromo supports event export in HepMC, ROOT, and SVG formats and provides a consistent interface for inspecting, filtering, and modifying particle collision events. This paper describes the architecture, typical use cases, and performance characteristics of Chromo and its role in contemporary astroparticle simulations, such as in the MCEq cascade solver.

###### keywords:

## 1 Introduction

Simulations of hadronic, photo-hadronic, and nuclear interactions are central to many problems in high-energy physics. At colliders, event generators are employed to model the underlying event and soft interactions in analyses involving nuclear targets. In cosmic-ray and neutrino physics, these interactions determine air shower development and atmospheric lepton fluxes. Accurate modeling across wide energy and phase space ranges, especially in the forward region, often requires combining multiple event generators and estimating uncertainties through inter-model comparisons.

Despite decades of development, most general-purpose event generators, such as Pythia[ [1](https://arxiv.org/html/2507.21856v1#bib.bib1) , [2](https://arxiv.org/html/2507.21856v1#bib.bib2) ] , DPMJet[ [3](https://arxiv.org/html/2507.21856v1#bib.bib3) , [4](https://arxiv.org/html/2507.21856v1#bib.bib4) , [5](https://arxiv.org/html/2507.21856v1#bib.bib5) ] , QGSJet[ [6](https://arxiv.org/html/2507.21856v1#bib.bib6) , [7](https://arxiv.org/html/2507.21856v1#bib.bib7) , [8](https://arxiv.org/html/2507.21856v1#bib.bib8) , [9](https://arxiv.org/html/2507.21856v1#bib.bib9) ] , EPOS[ [10](https://arxiv.org/html/2507.21856v1#bib.bib10) , [11](https://arxiv.org/html/2507.21856v1#bib.bib11) ] , Sibyll[ [12](https://arxiv.org/html/2507.21856v1#bib.bib12) , [13](https://arxiv.org/html/2507.21856v1#bib.bib13) , [14](https://arxiv.org/html/2507.21856v1#bib.bib14) ] , remain fragmented in interface design, configuration mechanisms, and output formats. This heterogeneity hinders interoperability and efficient model comparison. Existing wrappers like CRMC[ [15](https://arxiv.org/html/2507.21856v1#bib.bib15) ] simplify some aspects but are limited in scope, lack a modern interface, and require substantial setup effort.

To address these challenges, we present the open-source package 111 [https://github.com/impy-project/chromo](https://github.com/impy-project/chromo)Chromo [ [16](https://arxiv.org/html/2507.21856v1#bib.bib16) ] , a Cosmic ray and HadRonic interactiOn MOnte carlo frontend – implemented in Python. It aims to reduce the friction of using these tools by providing a unified and user-friendly interface for simulation and analysis. Chromo is designed with three primary goals: (1) eliminate the need for platform-specific compilation through binary wheels; (2) enable interactive and script-based usage via a Pythonic API and Jupyter support; and (3) preserve high performance while offering flexible event manipulation, filtering, and export.

## 2 Overview

Chromo acts as a lightweight frontend to a curated collection of hadronic interaction models written in Fortran 77, Fortran 90, or C++. These include legacy models like Sibyll-2.1 , widely-used collider-focused tools like Pythia 8 , and multipurpose models like EPOS-LHC and DPMJet . Each model is bundled as a Python extension module compiled with f2py or pybind11 , with standardized initialization, kinematics configuration, event generation, and output logic.

### 2.1 Scientific applications

The unified interface provided by Chromo allows users to compare interaction models under identical conditions, which is critical for systematic studies. A prominent use case is the generation of particle production matrices used by the MCEq cascade solver to compute atmospheric lepton fluxes. In collider physics, Chromo serves as a drop-in replacement for CRMC , with added capabilities for visualization and custom analysis in Python.

### 2.2 Installation and distribution

For regular users, installation of Chromo is straightforward and requires no compilation from source. The package is distributed through the Python Package Index (PyPI) as platform-specific binary wheels, allowing users to install it simply by running:

This eliminates the need to manually compile Fortran or C++ code, which can be a significant barrier for non-expert users. Continuous integration workflows using GitHub Actions and cibuildwheel ensure that validated builds are available for all supported platforms (Linux, macOS, and Windows).

### 2.3 Interactive and scripted use

Chromo is equally suited for command-line use, scripting, and interactive sessions in Jupyter. The API follows Python conventions and provides introspectable classes for kinematics, event generators, and events. Generated events can be streamed, filtered, visualized as SVG graphs, or written to HepMC3 and ROOT formats for downstream analysis.

### 2.4 Zero-overhead integration

The internal design leverages memory views and Fortran common blocks to expose event information directly as NumPy arrays, avoiding unnecessary copying. As shown in later performance benchmarks, this allows Chromo to match or even outperform traditional wrappers, especially for fast generators like Sibyll .

### 2.5 Basic example

A typical workflow involves setting up the initial state of a collision using the CenterOfMass or FixedTarget classes from the kinematics module, initializing a model, and streaming events:

Users can filter events, export to disk, or visualize them interactively. The event objects expose particle data as NumPy arrays and include metadata for reproducibility.

## 3 Example usage

This section illustrates how Chromo can be used to simulate events, analyze particle properties, and export data, all within a modern Pythonic workflow. The design emphasizes ease of use for both quick interactive exploration and large-scale data production.

### 3.1 Basic workflow

A typical workflow begins by defining the collision kinematics and selecting an event generator. Chromo provides specialized classes to encode frame-specific configurations:

### 3.2 Particle filtering and derived quantities

Each event object provides NumPy views to HEPEVT-style data. Common operations include filtering, histogramming, and calculating derived observables:

No data is copied unless explicitly requested. The default interface is optimized for memory locality and allows event filtering via boolean masks.

### 3.3 Working with composite targets

In many applications, such as air shower simulations or fixed-target experiments, the target may consist of a mixture of nuclei. Chromo supports this use case through the CompositeTarget class, which allows users to define a probabilistic mixture of nuclei:

Internally, Chromo samples target nuclei from a multinomial distribution according to their specified weights. To minimize initialization overhead, which can be significant for some generators, Chromo precomputes the number of events to simulate for each target nucleus and processes them in contiguous blocks. This avoids multiple re-initialization of the generator with different nuclear targets.

### 3.4 A mini-analysis

The following example demonstrates a mini-analysis: generating events, filtering final-state particles, histogramming key observables, and visualizing the result. It illustrates Chromo’s native compatibility with the scientific Python stack.

This recipe produces histograms similar to those shown in Figure [1](https://arxiv.org/html/2507.21856v1#S3.F1) .

### 3.5 Model switching and parameter scans

All event generator classes in Chromo inherit from a common base class MCRun , which allows seamless switching between different models. For example, one can loop through models to compare results across them:

Because MCRun defines a writable .kinematics attribute, you can reset collision parameters, such as center‑of‑mass energy or projectile/target nuclei, on the fly without reinitializing the generator:

Note that while some generators tolerate increasing the energy on the fly, others (e.g., Phojet or the DPMJet family) construct internal lookup tables only up to the energy specified at initialization and will abort if higher energies are requested. To ensure consistent behavior when switching between models or varying the energy, each generator should be initialized with the maximum energy and heaviest nuclei intended for the study.

Each generator model can be initialized only once per Python process. A second instantiation causes Chromo to abort, as the underlying Fortran libraries are dynamically loaded into memory and cannot be unloaded or re-initialized within the same session. Reconstructing a generator class from the same module merely reuses the already loaded shared library. If its initialization routine is invoked again, most generators will fail.

To avoid such conflicts and enable safe concurrent execution, each model should be run in a separate Python process. This can be achieved using Python’s multiprocessing module with maxtasksperchild=1 , ensuring that each worker process initializes exactly one model and then exits. This allows multiple instances of the same or different generators to run in parallel without shared-library interference:

### 3.6 Definition of stable particles

In both air-shower and collider simulations, the definition of “stable” particles depends on the context and specific analysis goals. Chromo allows this behavior to be explicitly configured through its generator interface.

Each generator provides the methods set_stable(pid) and set_unstable(pid) , which allow users to mark particles identified by their PDG ID as either stable (to be included in the final state) or unstable (to be decayed, if supported by the generator):

Not all generators natively support the decay of unstable particles. In particular, models from the QGSJet family may return certain particles undecayed, even if explicitly marked as unstable. For such cases, Chromo provides an optional fallback mechanism via the DecayHandler class, which uses Pythia 8 to decay remaining unstable particles and update the event record. This handler is enabled by default only for QGSJet models, but not for others, as most generators implement their own internal decay logic. If particles marked as unstable remain in the final state, Chromo will issue a warning. In such cases, users can manually enable the decay handler as follows:

The generator has useful property final_state_particles that returns a tuple of PDG IDs considered stable by the generator. This property can also be assigned a new list of PDG IDs to redefine the final state according to the needs of the analysis. For example, to declare all particles with lifetimes longer than a given threshold (e.g., $$ 10−1810^{-18}10 start_POSTSUPERSCRIPT - 18 end_POSTSUPERSCRIPT $$ sec) as stable, the following utility function can be used:

This mechanism provides fine-grained and consistent control over decay behavior across different models and facilitates reproducible event selection criteria.

### 3.7 Accessing cross sections

Chromo provides direct access to total and partial cross sections computed by the event generators. This is useful for normalizing event weights, studying energy-dependent behavior, or validating model consistency against external data.

Each generator implements a cross_section() method that returns a CrossSectionData object. This object contains fields such as total, inelastic, and elastic cross sections, as well as various diffractive components. All values are expressed in millibarns (mb), where available. If a generator does not provide a particular cross section, the corresponding attribute is set to NaN .

The cross section API is generator-agnostic. Internally, values are either computed dynamically (e.g., in DPMJet ) or taken from pre-tabulated data (e.g., in Sibyll and QGSJet ). Figure [2](https://arxiv.org/html/2507.21856v1#S3.F2) illustrates the energy dependence of various cross section components in $$ p​pppitalic_p italic_p $$ collisions for selected models, including total, inelastic, and diffractive contributions.

### 3.8 Event serialization

Generated events can be serialized to HepMC, ROOT (via uproot ), or SVG formats using dedicated writer classes. Each writer can be used as a context manager to ensure proper resource handling and automatic file closing. It is possible to combine multiple writers to simultaneously write events in all three available formats:

Events include metadata such as model version, random number generator (RNG) seed, and kinematic configuration to ensure reproducibility.

### 3.9 Event inspection and visualization

Printing an event with print(event) shows the raw HepEvt record, a compact Fortran data structure. While efficient, it is not easy to interpret or follow the particle history. Some generators, such as Pythia 6, provide full event histories including intermediate and decayed particles, making them suitable for graphical inspection.

In Jupyter Notebooks, events objects of type EventData are automatically visualized as directed graphs when placed at the end of a cell:

An example graph is shown in Figure [3](https://arxiv.org/html/2507.21856v1#S3.F3) for an $$ s=15\sqrt{s}=15\,square-root start_ARG italic_s end_ARG = 15 $$ GeV $$ p​pppitalic_p italic_p $$ collision. Because the output is rendered as rich HTML, one can hover the mouse over particles and vertices to reveal additional tooltip information. Such graphs can be automatically generated for models that expose the complete event generation history including intermediate states and decayed particles.

The automatic visualization is powered by the special method _repr_html_() , and relies on functionality provided by pyhepmc , which uses the optional graphviz package. To further manipulate or customize the visual output, one can use the full pyhepmc API directly. The same visualization backend is also used by the Svg writer, which exports event graphs to SVG files for use outside of Jupyter.

### 3.10 Using the command-line interface

Chromo includes a command-line interface (CLI) for running simulations without writing Python code. This interface is particularly useful for scripted workflows and batch production. A typical command looks like this:

This generates 1000 proton–oxygen collisions at $$ s=5​TeV\sqrt{s}=5\,\mathrm{TeV}square-root start_ARG italic_s end_ARG = 5 roman_TeV $$ using the Sibyll-2.3d model and writes the output in HepMC3 format.

Frequently used CLI options:

-n , --number – number of events to generate

-m , --model – interaction model (tolerant string match)

-S , --sqrts – center-of-mass energy $$ s\sqrt{s}square-root start_ARG italic_s end_ARG $$ in GeV

-i , --projectile-id – projectile (e.g., p , pi+ , PDG code)

-I , --target-id – target (e.g., O , N , Pb )

-f , --out – output file name (format is inferred from extension)

-o , --output – explicit output format ( hepmc , hepmc:gz , root , root:vertex , svg (default is hepmc ))

-s , --seed – random seed (0 means random seed)

-h , --help – show help message and exit

Internally, the CLI constructs the appropriate kinematic configuration, initializes the selected model, and writes events using the same writer backend as the Python API. Model-specific parameters can also be customized using a Python-based configuration file via --config . The CLI mimics the behavior of CRMC[ [15](https://arxiv.org/html/2507.21856v1#bib.bib15) ] to facilitate compatibility between these two tools, and to enable deployments in production environments.

## 4 Software architecture

Chromo is built around three major abstractions: EventKinematics , MCRun , and MCEvent . The architecture is illustrated in Figure [4](https://arxiv.org/html/2507.21856v1#S4.F4) .

### 4.1 Kinematics module

The kinematics module provides classes and functions for specifying and manipulating with the initial state of particle interactions in a structured way. The base class EventKinematicsBase stores all relevant information such as incoming particle IDs, energy, momentum, and frame type.

The two basic specializations are EventKinematicsWithRestframe and EventKinematicsMassless where the latter handles the case of collisions between massless particles like photons. The beam argument in these two generic classes expects a pair of arrays of ( $$ pμparticle1p_{\mu}^{\text{particle1}}italic_p start_POSTSUBSCRIPT italic_μ end_POSTSUBSCRIPT start_POSTSUPERSCRIPT particle1 end_POSTSUPERSCRIPT $$ , $$ pμparticle2p_{\mu}^{\text{particle2}}italic_p start_POSTSUBSCRIPT italic_μ end_POSTSUBSCRIPT start_POSTSUPERSCRIPT particle2 end_POSTSUPERSCRIPT $$ ), however boosts are restricted to the z-direction except in the case of the PHOJET family of generators. Each kinematics object is frame-aware and supports automatic transformation of event four-vectors, making analysis and output formats consistent using the native generator versions for boosts where possible. The two convenience classes CenterOfMass and FixedTarget specialize the interface to most popular scenarios and restrict energy and frame parameters to suitable forms.

### 4.2 Middle layer, event wrapping, and data handling

Most Fortran-based event generators store their output in HEPEVT-style common blocks or provide interfaces for conversion into that format. In Chromo, generators from the QGSJet and Sibyll families, for example, use a dedicated Fortran middle layer to convert their internal event records into HEPEVT. This layer also offers a convenient extension point for additional customization in a compiled language.

The Python bindings for each generator are created using numpy.f2py , which exposes selected Fortran subroutines and makes common block memory directly accessible as NumPy arrays. This enables efficient zero-copy access to particle stacks, including the HEPEVT structure. Chromo reads from these shared-memory regions via NumPy views, ensuring that data is only copied when explicitly requested.

The EventData class wraps these arrays and provides a high-level, NumPy-compatible interface. It supports slicing, filtering, and derived kinematic quantities such as transverse momentum and rapidity, all implemented using vectorized operations for performance and clarity.

When users follow idiomatic NumPy practices, the Python overhead in Chromo is negligible. For example, selecting charged pions with $$ pT>0.5p_{T}>0.5italic_p start_POSTSUBSCRIPT italic_T end_POSTSUBSCRIPT > 0.5 $$ GeV and $$ |η|<2.5|\eta|<2.5| italic_η | < 2.5 $$ can be expressed compactly and efficiently:

By contrast, using patterns inspired by compiled languages, such as explicit loops over particles, incurs unnecessary overhead and should be avoided:

Even in cases where copies of event data are unavoidable (e.g., due to fancy indexing), the overhead is typically small compared to the cost of generating events.

### 4.3 Custom pybind11 interface for Pythia 8

In analogy to the Fortran-based middle layer, Chromo includes a custom Python wrapper for the C++-based Pythia 8 event generator, implemented using pybind11 . 222 See [https://github.com/pybind/pybind11](https://github.com/pybind/pybind11) Unlike the official Pythia 8 Python bindings, which expose particle information via per-particle accessors, our implementation provides direct NumPy access to entire particle arrays, including four-momenta and auxiliary attributes. This design enables fully vectorized event processing in Python and avoids the overhead associated with Python-level loops and repeated function calls.

Internally, the C++ event data structure follows a layout analogous to HEPEVT, with raw pointer access to the contiguous particle stack. This allows the full event to be transferred to Python in a single call, without copying individual particles or fields.

One of the distinctive features of Pythia 8 is its flexible configuration system, which accepts a list of key-value strings. Chromo exposes this interface directly via the config keyword. This covers a wide range of Pythia 8 use cases without modifying the C++ interface. By default, Chromo sets SoftQCD: inelastic = on to match the “minimum bias” behavior of the other generators.

To specify a custom configuration, the following pattern can be used:

This interface allows users to reuse examples and configurations directly from the official Pythia 8 documentation. However, the current implementation is not yet a complete replacement for the native interface. Additionally, since Pythia 8 does not validate configuration keys or argument types, incorrect settings may lead to segmentation faults that originate in the Pythia 8 backend and are not caught by Chromo.

### 4.4 Random number generators and seeds

Random number generators (RNGs) are a core component of all event generators, directly affecting reproducibility and statistical properties of simulations. Most Fortran-based generators bundled with Chromo rely on the RANMAR algorithm [ [17](https://arxiv.org/html/2507.21856v1#bib.bib17) ] , distributed via CERNLIB [ [18](https://arxiv.org/html/2507.21856v1#bib.bib18) ] . In contrast, Pythia8 employs its own Mersenne Twister implementation [ [19](https://arxiv.org/html/2507.21856v1#bib.bib19) ] .

To ensure consistent and reproducible behavior across models, Chromo overrides each generator’s internal RNG with a shared interface to numpy.random.Generator , using the PCG-64 backend [ [20](https://arxiv.org/html/2507.21856v1#bib.bib20) ] . This enables transparent seeding and state serialization, including in workflows where random numbers are consumed outside of the Fortran/C++ code, such as when sampling over CompositeTarget s in Python space. The serialization of the RNG state allows for the exact reproduction of events or for continuation from a specific point without accessing the often cryptic interfaces of the original libraries.

### 4.5 Writers and exporters

Output writers are available for HepMC3 , ROOT (via uproot ), and SVG. Each writer implements a simple interface:

Writers can be used inside Python scripts or through the CLI frontend, which mimics CRMC ’s behavior while offering a more portable and transparent configuration mechanism.

### 4.6 Supported interaction models

Chromo supports a wide range of hadronic interaction models, covering hadron–nucleon ( $$ h​NhNitalic_h italic_N $$ ), hadron–nucleus ( $$ h​AhAitalic_h italic_A $$ ), nucleus–nucleus ( $$ A​AAAitalic_A italic_A $$ ), photon–nucleon ( $$ γ​N\gamma Nitalic_γ italic_N $$ ), photon–photon ( $$ γ​γ\gamma\gammaitalic_γ italic_γ $$ ), and electron–positron ( $$ e​eeeitalic_e italic_e $$ ) collisions. Table [1](https://arxiv.org/html/2507.21856v1#S4.T1) summarizes each model’s projectile/target coverage, notable limitations, and event generation performance relative to PYTHIA 8 for 14 TeV proton–proton collisions.

$$ hhitalic_h $$ = hadron, $$ NNitalic_N $$ = nucleon (p or n), $$ AAitalic_A $$ = nucleus, $$ γ\gammaitalic_γ $$ = photon, $$ eeitalic_e $$ = electron/positron

Not available on Windows.

Includes versions 2.3/2.3c/2.3d/2.3e.

Based on 2.3e.

## 5 Performance

We benchmark Chromo against CRMC by generating proton–proton events over a wide range of center-of-mass energies using several hadronic interaction models: SIBYLL-2.3d (2.3e in CRMC), DPMJET-III-19.1, QGSJet-III, and EPOS-LHCR (with and without hadronic rescattering). Across all energies and models, Chromo matches or exceeds CRMC’s event generation rates (see Fig. [5](https://arxiv.org/html/2507.21856v1#S5.F5) ). Note that CRMC is compiled in Release mode at - O3 optimization level (instead of the default - O0 ) to match Chromo’s defaults. These results demonstrate that a high-level interface implemented in Python can deliver competitive performance when carefully designed bindings and memory sharing are employed.

## 6 Validation and testing

Chromo is validated through an extensive test suite comprised of almost 2,000 unit tests. These tests are executed via continuous integration (CI) using GitHub Actions across all supported platforms including Linux, macOS, and Windows and for all Python versions from 3.9 onward. Because event generators incorporate random number generation and floating-point arithmetic, bitwise identical results cannot be expected across architectures or platforms. To address this, Chromo employs probabilistic tests that compare statistical properties of generated events against known reference distributions. The tests verify model correctness while tolerating minor numerical variation. All changes to the codebase are automatically validated in CI to ensure platform-independent consistency, API stability, and reproducibility.

## 7 Conclusion and outlook

We have presented Chromo , a unified Python interface to a comprehensive suite of hadronic interaction event generators, including EPOS , DPMJet , Sibyll , QGSJet , and Pythia . Through careful design of zero-copy bindings, efficient common-block access, and integration with the Scientific Python ecosystem, Chromo achieves performance comparable to or exceeding that of existing wrappers such as CRMC, while offering a high-level, user-friendly API. We have demonstrated a variety of use cases and shown how the package simplifies model comparison, parameter scans, and interactive analysis in Jupyter notebooks.

Chromo is distributed as easy-to-install binary packages, removing the need for manual compilation or dependency management. It addresses longstanding fragmentation in event generator interfaces, configuration styles, and data formats through a unified, high-level API and shared data structures. Its interface enables uniform handling of setup, generation, filtering, and export, reducing boilerplate and lowering the entry barrier for new users. Rigorous probabilistic unit tests and continuous integration ensure reproducibility and cross-platform stability.

Looking ahead, Chromo can continue to evolve in several directions to better support the particle and astroparticle physics communities. Expanding the range of supported event generators and data formats will further increase its utility, especially through the inclusion of specialized models and additional types of particle interactions.

## Acknowledgements

We thank the developers of the Fortran and C++ event generator codes for their support in interface development. We also gratefully acknowledge the invaluable contributions of early adopters, including Felix Riehn, Keito Watanabe, Sonia El Hedri, Tetiana Kozynets, Dennis Soldin, and members of the LHCb collaboration. AF and AP acknowledge support from Academia Sinica (Grant No. AS-GCS-113-M04) and the National Science and Technology Council (Grant No. 113-2112-M-001-060-MY3).

## References
