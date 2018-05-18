#!python2
# coding: utf-8

"""
EQUATIONS
Functions used to define variation in time of several simulation related parameters
"""

__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David']


def bacteria_density_eq(previous_density, growth_rate, lymphocyte_inhibition, total_immune_cells, antibiotic_inhibition,
                        antibiotic_uptake, antibiotic_concentration, time_step=1/(24*60.0)):
    """
    ref: Gjini, E., & Brito, P. H. (2016)
         Integrating Antimicrobial Therapy with Host Immunity to Fight Drug-Resistant Infections: Classical vs. Adaptive
         Treatment. PLOS Computational Biology, 12(4), e1004857
         http://doi.org/10.1371/journal.pcbi.1004857

    New antibiotic sensitive/resistant Bacteria density after time_step
    new_B = B + (rB - dBI - δBη(t)Aₘ) * Δt

    PARAMETERS:
        previous_density : int/float
            B, previous antibiotic sensitive/resistant bacteria density
            DEFAULT INITIAL VALUE = 10 (sensitive), 2 (resistant)
            RANGE = << immune_response_half_max_growth (parameter of other equations)
        growth_rate : int/float
            r, growth rate of antibiotic sensitive/resistant bacteria
            DEFAULT = 3.3 (sensitive), 1.1 (resistant)
            RANGE = 1-8 (sensitive), <= sensitive (resistant)
        lymphocyte_inhibition : int/float
            d, rate at which lymphocytes kill bacteria
            DEFAULT = 10**-5
            RANGE = (10**-5)-(10**-4)
        total_immune_cells : int/float
            I, total immune system cells -> N (naive precursor cells), E (effector cells) and M (memory cells)
        antibiotic_inhibition : int/float
            δ, rate at which antibiotic inhibits sensitive/resistant bacteria
            DEFAULT = 1 (sensitive), 0.1 (resistant)
            RANGE = 1 (sensitive), 0-sensitive (resistant)
        antibiotic_uptake : int
            η(t), rate at which antibiotic is consumed, 0 or 1
        antibiotic_concentration : int/float
            Aₘ, mean antibiotic concentration, mg/l
            DEFAULT = 6
            RANGE = 0.03–128
        time_step : int/float
            steps per day
            DEFAULT = 1/(24*60) -> 1 minute

    RETURNS: float
        New sensitive/resistant bacteria density after time_step
    """
    # If there are less than 1 bacteria, then there are ~0 bacterias
    # (avoids bacteria "ressuscitation" while also avoiding zero division error)
    if previous_density < 1.0:
        previous_density = 0.0001

    return previous_density + ((growth_rate * previous_density -
                                lymphocyte_inhibition * previous_density * total_immune_cells -
                                antibiotic_inhibition * previous_density * antibiotic_uptake * antibiotic_concentration)
                               * time_step)


def naive_precursor_cells_density_eq(previous_density, proliferation_rate, bacteria_density,
                                     immune_response_half_max_growth, time_step=1/(24*60.0)):
    """
    ref: Gjini, E., & Brito, P. H. (2016)
         Integrating Antimicrobial Therapy with Host Immunity to Fight Drug-Resistant Infections: Classical vs. Adaptive
         Treatment. PLOS Computational Biology, 12(4), e1004857
         http://doi.org/10.1371/journal.pcbi.1004857

    New naive precursor cells density after time_step
    new_N = N + (-σN * B/(k+B)) * Δt

    PARAMETERS:
        previous_density : int/float
            N, previous naive precursor cells density
            DEFAULT INITIAL VALUE = 200
            RANGE = 15-1500
        proliferation_rate : int/float
            σ, max proliferation rate of immune cells
            DEFAULT = 2
            RANGE = 1.2-3
        bacteria_density : int/float
            B, bacteria density (sensitive + resistant)
        immune_response_half_max_growth : int/float
            k, bacteria density at which the immune response grows at half its maximum rate
            DEFAULT = 10**5
            RANGE = (10**4)-(10**5)
        time_step : int/float
            steps per day
            DEFAULT = 1/(24*60) -> 1 minute

    RETURNS: float
        New naive precursor cells density after time_step
    """
    return previous_density + (((-1 * proliferation_rate) * previous_density *
                                (bacteria_density / (immune_response_half_max_growth + bacteria_density)))
                               * time_step)


def effector_cells_density_eq(previous_density, proliferation_rate, naive_precursor_cells_density, bacteria_density,
                              immune_response_half_max_growth, effector_decay, time_step=1/(24*60.0)):
    """
    ref: Gjini, E., & Brito, P. H. (2016)
         Integrating Antimicrobial Therapy with Host Immunity to Fight Drug-Resistant Infections: Classical vs. Adaptive
         Treatment. PLOS Computational Biology, 12(4), e1004857
         http://doi.org/10.1371/journal.pcbi.1004857

    New effector cells density after time_step
    new_E = E + ((2σN + σE) * B/(k+B) - hE * (1 - B/(k+B))) * Δt

    PARAMETERS:
        previous_density : int/float
            E, previous effector cells density
            DEFAULT INITIAL VALUE = 0
        proliferation_rate : int/float
            σ, max proliferation rate of immune cells
            DEFAULT = 2
            RANGE = 1.2-3
        naive_precursor_cells_density : int/float
            N, naive precursor cells density
        bacteria_density : int/float
            B, bacteria density (sensitive + resistant)
        immune_response_half_max_growth : int/float
            k, bacteria density at which the immune response grows at half its maximum rate
            DEFAULT = 10**5
            RANGE = (10**4)-(10**5)
        effector_decay : int/float
            h, max decay rate of effector cells
            DEFAULT = 0.35
            RANGE = 0.1-0.8
        time_step : int/float
            steps per day
            DEFAULT = 1/(24*60) -> 1 minute

    RETURNS: float
        New effector cells density after time_step
    """
    return previous_density + (((2 * proliferation_rate * naive_precursor_cells_density +
                                proliferation_rate * previous_density) *
                               (bacteria_density / (immune_response_half_max_growth + bacteria_density)) -
                                effector_decay * previous_density *
                                (1 - (bacteria_density / (immune_response_half_max_growth + bacteria_density))))
                               * time_step)


def memory_cells_density_eq(previous_density, converted_effectors, effector_cells_density, effector_decay,
                            bacteria_density, immune_response_half_max_growth, time_step=1/(24*60.0)):
    """
    ref: Gjini, E., & Brito, P. H. (2016)
         Integrating Antimicrobial Therapy with Host Immunity to Fight Drug-Resistant Infections: Classical vs. Adaptive
         Treatment. PLOS Computational Biology, 12(4), e1004857
         http://doi.org/10.1371/journal.pcbi.1004857

    New memory cells density after time_step
    new_M = M + (fEh * (1 - B/(k+B))) * Δt

    PARAMETERS:
        previous_density : int/float
            M, previous memory cells density
            DEFAULT INITIAL VALUE = 0
        converted_effectors : int/float
            f, fraction of effector cells which convert to memory cells
            DEFAULT = 0.1
            RANGE = 0.05-0.1
        effector_cells_density : int/float
            E, effector cells density
        effector_decay : int/float
            h, max decay rate of effector cells
            DEFAULT = 0.35
            RANGE = 0.1-0.8
        bacteria_density : int/float
            B, bacteria density (sensitive + resistant)
        immune_response_half_max_growth : int/float
            k, bacteria density at which the immune response grows at half its maximum rate
            DEFAULT = 10**5
            RANGE = (10**4)-(10**5)
        time_step : int/float
            steps per day
            DEFAULT = 1/(24*60) -> 1 minute

    RETURNS: float
        New memory cells density after time_step
    """
    return previous_density + ((converted_effectors * effector_cells_density * effector_decay *
                                (1 - (bacteria_density / (immune_response_half_max_growth + bacteria_density))))
                               * time_step)


def antibiotic_uptake_eq(treatment_type, **kwargs):
    """
    ref: Gjini, E., & Brito, P. H. (2016)
         Integrating Antimicrobial Therapy with Host Immunity to Fight Drug-Resistant Infections: Classical vs. Adaptive
         Treatment. PLOS Computational Biology, 12(4), e1004857
         http://doi.org/10.1371/journal.pcbi.1004857

    Antibiotic uptake function which governs the antibiotic_uptake value of bacteria_density_eq()

    Classic Treatment:
           { 1 if t₁ <= t <= t₁+t₂
    η(t) = {
           { 0 if t < t₁ or t > t₁+t₂

    Adaptive Treatment:
           { 1 if B(t) >= Ω
    η(t) = {
           { 0 if B(t) < Ω

    PARAMETERS:
        treatment_type : str
            'Classic', 'Adaptive' or 'User', representing the type of treatment
        kwargs
            Depending on the value of treatment_type, kwargs expects different values:

            treatment_type == 'Classic':
                delay : int/float
                    t₁, initial time delay before starting treatment
                    DEFAULT = 3.5
                    RANGE = >= 0
                duration : int/float
                    t₂, duration of treatment
                    DEFAULT = 7
                    RANGE = >= 0
                time : int/float
                    t, time point of the simulation
                    DEFAULT INITIAL VALUE = 0
                    RANGE = >= 0

            treatment_type == 'Adaptive':
                bacteria_density_causing_symptoms : int/float
                    Ω, Density of total bacteria which causes symptoms to appear
                    DEFAULT = 10**6
                    RANGE = (10**3)-(10**7)
                total_bacteria_density : int/float
                    B, Total bacteria density (Bs + Br)

            treatment_type == 'User':
                taking_antibiotic : bool
                    True or False if antibiotic is being administred or not

    RETURNS: int
        0 or 1, representing antibiotic uptake for the given time step
    """
    if treatment_type == "Classic":
        delay = kwargs["delay"]
        duration = kwargs["duration"]
        time = kwargs["time"]

        # treatment occurs between delay and duration + delay
        return int(delay <= time <= delay + duration)  # 0 or 1

    elif treatment_type == "Adaptive":
        bacteria_density_causing_symptoms = kwargs["bacteria_density_causing_symptoms"]
        total_bacteria_density = kwargs["total_bacteria_density"]

        # treatment occurs every time the bacteria reach a density above the set threshold
        return int(total_bacteria_density >= bacteria_density_causing_symptoms)  # 0 or 1

    elif treatment_type == "User":
        return int(kwargs["taking_antibiotic"])  # 0 or 1


def calculate_next_time_step(current_time_point, sensitive_bacteria_density, resistant_bacteria_density,
                             naive_precursor_cells_density, effector_cells_density, memory_cells_density,
                             immune_cells_proliferation_rate, lymphocyte_inhibition, converted_effectors,
                             effector_cells_decay, antibiotic_concentration, immune_response_half_max_growth,
                             antibiotic_treatment_type, antibiotic_uptake_args, bs_variables, br_variables,
                             time_step=1/(24*60.0)):
    """
    Calculates all equations, using the previous values, for the given time_step

    PARAMETERS:
        current_time_point : float
            current timepoint of simulation
        sensitive_bacteria_density : int/float
            previous sensitive Bacteria density
        resistant_bacteria_density : int/float or None
            previous resistant Bacteria density
        naive_precursor_cells_density : int/float
            previous naive precursor cells density
        effector_cells_density : int/float
            previous effector cells density
        memory_cells_density : int/float
            previous memory cells density
        immune_cells_proliferation_rate : int/float
            max proliferation rate of immune cells
        lymphocyte_inhibition : int/float
            rate at which lymphocyte kill bacteria
        converted_effectors : int/float
            fraction of effector cells which convert to memory cells
        effector_cells_decay : int/float
            max decay rate of effector cells
        antibiotic_concentration : int/float
            previous antibiotic concentration
        immune_response_half_max_growth : int/float
            bacteria density at which the immune response grows at half its maximum rate
        antibiotic_treatment_type : str
            'Classic', 'Adaptive' and 'User', representing the type of treatment
        antibiotic_uptake_args : dict
            kwargs arguments used in antibiotic_uptake_eq(), depending on the type of treatment
        bs_variables : tuple of floats
            tuple with every bacteria_density_eq function variable for sensitive bacteria
            (except other parameters already used in this function), in order
        br_variables : tuple of floats
            tuple with every bacteria_density_eq function variable for resistant bacteria
            (except other parameters already used in this function), in order
        time_step : int/float
            x/(24*60) (step per day) (defaults to 1 minute)

    RETURNS: (new_time_point, new_bs, new_br, new_n, new_e, new_m), each element as float
        Each new value, using the previous values, for one time step
    """
    total_bacteria_density = sensitive_bacteria_density + resistant_bacteria_density

    if antibiotic_treatment_type == 'Classic':
        antibiotic_uptake_args["time"] = current_time_point
    if antibiotic_treatment_type == "Adaptive":
        antibiotic_uptake_args["total_bacteria_density"] = total_bacteria_density

    antibiotic_uptake = antibiotic_uptake_eq(antibiotic_treatment_type, **antibiotic_uptake_args)
    total_immune_cells = naive_precursor_cells_density + effector_cells_density + memory_cells_density

    # bs and br variables = growth_rate, antibiotic_inhibition
    new_bs = bacteria_density_eq(sensitive_bacteria_density, bs_variables[0], lymphocyte_inhibition,
                                 total_immune_cells, bs_variables[1], antibiotic_uptake, antibiotic_concentration,
                                 time_step)
    new_br = bacteria_density_eq(resistant_bacteria_density, br_variables[0], lymphocyte_inhibition,
                                 total_immune_cells, br_variables[1], antibiotic_uptake, antibiotic_concentration,
                                 time_step)
    new_n = naive_precursor_cells_density_eq(naive_precursor_cells_density, immune_cells_proliferation_rate,
                                             total_bacteria_density, immune_response_half_max_growth, time_step)
    new_e = effector_cells_density_eq(effector_cells_density, immune_cells_proliferation_rate,
                                      naive_precursor_cells_density, total_bacteria_density,
                                      immune_response_half_max_growth, effector_cells_decay, time_step)
    new_m = memory_cells_density_eq(memory_cells_density, converted_effectors, effector_cells_density,
                                    effector_cells_decay, total_bacteria_density, immune_response_half_max_growth,
                                    time_step)

    new_time_point = current_time_point + time_step
    return new_time_point, new_bs, new_br, new_n, new_e, new_m


###############################
# Scenario 2 specific equations
###############################

def nutrient_concentration_eq(previous_concentration, flow_rate, nutrients_for_bacteria_duplication,
                              bacteria_growth_rate, bacteria_density, half_saturation, time_step=1/(24*60.0)):
    """
    Chemostat equation for nutrient concentration
    
    New nutrient concentration after time_step
    new_N = N + (ωN₀ - εψ*Bd*(N/(Q+N)) - ωN) * Δt
    
    PARAMETERS:
        previous_concentration : int/float
            N, previous nutrient concentration
        flow_rate : int/float
            ω, rate of nutrient flow
        nutrients_for_bacteria_duplication : int/float
            ε, nutrients necessary for bacteria duplication
        bacteria_growth_rate : int/float
            ψ, growth rate of bacteria
        bacteria_density : int/float
            Bd, current bacteria density
        half_saturation : int/float
            Q, constant that makes (N/(Q+N)) = 1/2 when Q=C
        time_step : int/float
            steps per day
            DEFAULT = 1/(24*60) -> 1 minute
            
    RETURNS: float
        New nutrient concentration after time_step
    """
    # ω (flow_rate) is usually 0.01
    # Q (half_saturation) is usually 5

    initial_concentration = 100

    return previous_concentration + (flow_rate * initial_concentration -
                                     nutrients_for_bacteria_duplication * bacteria_growth_rate * bacteria_density *
                                     previous_concentration / (half_saturation + previous_concentration) -
                                     flow_rate * previous_concentration) * time_step


def nutrients_for_bacteria_duplication_eq(bacteria_growth_rate, flow_rate, half_saturation, stable_bacteria_density):
    """
    Calculates the necessary nutrients for bacteria duplication (ε) that enables bacteria to have a stable density of
    stable_bacteria_density
    
    ε = (N(ψ - ω) - Qω) / Bd(ψ - ω)
    
    PARAMETERS:
        bacteria_growth_rate : int/float
            ψ, growth rate of bacteria
        flow_rate : int/float
            ω, rate of nutrient flow
        half_saturation : int/float
            Q, constant that makes (N/(Q+N)) = 1/2 when Q=C
        stable_bacteria_density : int
            Bd, density at which bacteria is supposed to be stable
    
    RETURNS: float
        Necessary nutrients for bacteria duplication (ε)
    """
    initial_concentration = 100

    return ((initial_concentration * (bacteria_growth_rate - flow_rate) - half_saturation * flow_rate) /
            (stable_bacteria_density * (bacteria_growth_rate - flow_rate)))


def multiple_antibiotic_bacteria_density_eq(previous_density, growth_rate, lymphocyte_inhibition, total_immune_cells,
                                            antibiotic_inhibition_dict, nutrient_concentration, half_saturation,
                                            flow_rate, time_step=1/(24*60.0)):
    """
    Based on bacteria_density_eq() and Monod equations
    Allows several antibiotics
    
    ref: Gjini, E., & Brito, P. H. (2016)
         Integrating Antimicrobial Therapy with Host Immunity to Fight Drug-Resistant Infections: Classical vs. Adaptive
         Treatment. PLOS Computational Biology, 12(4), e1004857
         http://doi.org/10.1371/journal.pcbi.1004857

    New Bacteria density after time_step
    new_B = B + (rB*[C/(Q+C)] - ωB - dBI - δBη(t)Aₘ) * Δt

    PARAMETERS:
        previous_density : int/float
            B, previous bacteria density
            RANGE = << immune_response_half_max_growth (parameter of other equations)
        growth_rate : int/float
            r, growth rate of bacteria
            RANGE = 1-8
        lymphocyte_inhibition : int/float
            d, rate at which lymphocytes kill bacteria
            RANGE = (10**-5)-(10**-4)
        total_immune_cells : int/float
            I, total immune system cells -> N (naive precursor cells), E (effector cells) and M (memory cells)
        antibiotic_inhibition_dict : dict[dict[float, float, float]]
            Antibiotic inhibition, uptake and concentration values for each available antibiotic
                Inhibition:
                    δ, rate at which antibiotic inhibits bacteria
                    RANGE = 0-1
                Uptake:
                    η(t), rate at which antibiotic is consumed, 0 or 1
                Concentration:
                    Aₘ, mean antibiotic concentration, mg/l
                    DEFAULT = 6
                    RANGE = 0.03–128
            {"antibiotic1: {"inhibition": float, "uptake": float, "concentration": float}, ...}
        nutrient_concentration : float
            C, nutrient concentration (chemostat variable)
        half_saturation : int/float
            Q, constant that makes (N/(Q+N)) = 1/2 when Q=C
        flow_rate : int/float
            ω, rate of nutrient flow
        time_step : int/float
            steps per day
            DEFAULT = 1/(24*60) -> 1 minute

    RETURNS: float
        New bacteria density after time_step
    """
    # If there are less than 1 bacteria, then there are ~0 bacterias
    # (avoids bacteria "ressuscitation" while also avoiding zero division error)
    if previous_density < 1.0:
        previous_density = 0.0001

    # sums all (antibiotic_inhibition * antibiotic_uptake * antibiotic_concentration)
    antibiotic_value = 0
    for values_dict in antibiotic_inhibition_dict.itervalues():
        antibiotic_value += reduce(lambda x, y: x*y, values_dict.itervalues())

    return previous_density + ((growth_rate * previous_density *
                                (nutrient_concentration / (half_saturation + nutrient_concentration)) -
                                flow_rate * previous_density -
                                lymphocyte_inhibition * previous_density * total_immune_cells -
                                previous_density * antibiotic_value) *
                               time_step)


def calculate_next_time_step_scenario2(current_time_point, bacteria_densities, bacteria_growth_rate,
                                       bacteria_antibiotic_inhibition, antibiotics_concentrations, antibiotic_uptakes,
                                       nutrient_concentration_dict, flow_rate, nutrients_for_bacteria_duplication_dict,
                                       half_saturation, time_step=1/(24*60.0)):
    """
    Calculates bacterial growth in a microbiome, using the previous values, for the given time_step

    PARAMETERS:
        current_time_point : float
            current timepoint of simulation
        bacteria_densities : dict[float]
            each bacteria's density, {"bacteria": float}
        bacteria_growth_rate : dict[float]
            each bacteria's growth_rate, {"bacteria": float}
        bacteria_antibiotic_inhibition : dict[dict[float]]
            each bacteria's inhibition parameter for each antibiotic
            {"bacteria": {"antibiotic_1": float, "antibiotic_2": float, ...}, ...}
        antibiotics_concentrations : dict[dict[float]
            dictionary having the concentration of each antibiotic
            {"antibiotic_1": float, ...}
        antibiotic_uptakes : dict[dict[int]]
            dictionary having the uptake status of each antibiotic
            {"antibiotic_1": int(0 or 1), ...}
        nutrient_concentration_dict : dict[int/float]
            nutrient concentration for each bacteria
            {"bacteria": float}
        flow_rate : int/float
            rate of nutrient flow
        nutrients_for_bacteria_duplication_dict : dict[int/float]
            dictionary having the nutrients necessary for bacteria duplication for each bacteria
            {"bacteria": float}
        half_saturation : int/float
            constant that makes (N/(Q+N)) = 1/2 when Q=C
        time_step : int/float
            x/(24*60) (step per day) (defaults to 1 minute)
    
    RETURNS: (new_time_point, new_bacteria_densities, new_nutrient_concentrations); as float and x2 dict[float]
        Each new value, using the previous values, for one time step
    """
    new_bacteria_densities = {}
    new_nutrient_concentrations = {}

    for bacteria, density in bacteria_densities.iteritems():
        growth_rate = bacteria_growth_rate[bacteria]
        nutrients_for_bacteria_duplication = nutrients_for_bacteria_duplication_dict[bacteria]

        antibiotic_dict = {}
        for antibiotic in antibiotics_concentrations:
            antibiotic_dict[antibiotic] = {}
            antibiotic_dict[antibiotic]["concentration"] = antibiotics_concentrations[antibiotic]
            antibiotic_dict[antibiotic]["uptake"] = antibiotic_uptakes[antibiotic]
            antibiotic_dict[antibiotic]["inhibition"] = bacteria_antibiotic_inhibition[bacteria][antibiotic]

        new_nutrient_concentrations[bacteria] = nutrient_concentration_eq(nutrient_concentration_dict[bacteria],
                                                                          flow_rate, nutrients_for_bacteria_duplication,
                                                                          growth_rate, density, half_saturation,
                                                                          time_step)

        nutrient = new_nutrient_concentrations[bacteria]

        new_bacteria_densities[bacteria] = multiple_antibiotic_bacteria_density_eq(density, growth_rate, 0, 0,
                                                                                   antibiotic_dict,
                                                                                   nutrient, half_saturation, flow_rate,
                                                                                   time_step)

    new_time_point = current_time_point + time_step
    return new_time_point, new_bacteria_densities, new_nutrient_concentrations
