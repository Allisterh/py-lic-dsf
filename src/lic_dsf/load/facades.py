"""Economist-facing load packages: thin wrappers over granular sheet parsers.

Edit inputs in the LIC-DSF Excel workbook, then call these functions to load
them into Python. Granular ``load_*`` helpers remain available for tests and
library internals but are not part of the documented economist API.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from lic_dsf.books.domestic.types import DomesticDebtInputs
from lic_dsf.load.domestic import load_domestic_debt_inputs
from lic_dsf.load.input6 import load_input6_standard
from lic_dsf.load.input7 import load_input7_residual_params
from lic_dsf.load.probability import load_distress_covariates
from lic_dsf.load.rating import (
    load_ci_summary,
    load_input1_market,
    load_trigger_flags,
)
from lic_dsf.load.realism import (
    load_capital_assumptions,
    load_imported_data,
    load_invest_growth_series,
    load_lic_program_distribution,
    load_multiplier_grid,
)
from lic_dsf.load.tailored import load_tailored_params
from lic_dsf.rating.workbook import CiSummarySnapshot, TriggerFlags
from lic_dsf.realism.types import (
    CapitalAssumptions,
    LicProgramDistribution,
    MultiplierAssumptions,
)
from lic_dsf.resfin.params import ResidualFinancingParams
from lic_dsf.scenario.probability import DistressCovariates
from lic_dsf.stress.shocks.tailored_params import TailoredParams

if TYPE_CHECKING:
    from lic_dsf.realism.imported import ImportedDataCatalog
    from lic_dsf.stress.types import Input6StandardParams


@dataclass(frozen=True)
class StressLoad:
    """Input 6 standard + Input 7 residual financing + tailored params."""

    input6: Input6StandardParams
    residual: ResidualFinancingParams
    tailored: TailoredParams


@dataclass(frozen=True)
class RatingLoad:
    """CI Summary, Trigger flags, and Input 1 market-access cells."""

    ci: CiSummarySnapshot
    triggers: TriggerFlags | None
    market_access: bool
    embi_spread: float | None


@dataclass(frozen=True)
class RealismLoad:
    """Realism sheet assumptions and imported-data vintages."""

    imported: ImportedDataCatalog
    capital: CapitalAssumptions
    multipliers: list[MultiplierAssumptions]
    lic_programs: LicProgramDistribution
    invest_growth: pd.Series


def load_domestic(path: str | Path) -> DomesticDebtInputs:
    """Load domestic-debt sheet inputs from a LIC-DSF workbook.

    Edit Dom / related sheets in Excel, save, then call this function.

    Args:
        path: Path to the LIC-DSF Excel workbook.

    Returns:
        `DomesticDebtInputs` for `DomesticDebtBook`.
    """
    return load_domestic_debt_inputs(path)


def load_stress(path: str | Path) -> StressLoad:
    """Load Input 6, Input 7 ResFin, and tailored-test parameters.

    Edit stress / residual-financing sheets in Excel, save, then call this
    function.

    Args:
        path: Path to the LIC-DSF Excel workbook.

    Returns:
        `StressLoad` with ``input6``, ``residual``, and ``tailored``.
    """
    return StressLoad(
        input6=load_input6_standard(path),
        residual=load_input7_residual_params(path),
        tailored=load_tailored_params(path),
    )


def load_rating(path: str | Path) -> RatingLoad:
    """Load CI Summary, Trigger flags, and Input 1 market-access inputs.

    Edit CI / Trigger / Input 1 in Excel, save, then call this function.

    Args:
        path: Path to the LIC-DSF Excel workbook.

    Returns:
        `RatingLoad` with ``ci``, ``triggers``, ``market_access``, and
        ``embi_spread``.
    """
    ci = load_ci_summary(path)
    triggers = load_trigger_flags(path, ci.country_code)
    market_access, embi_spread = load_input1_market(path)
    return RatingLoad(
        ci=ci,
        triggers=triggers,
        market_access=market_access,
        embi_spread=embi_spread,
    )


def load_realism(path: str | Path) -> RealismLoad:
    """Load Realism 1–4 assumptions and Imported-data vintages.

    Edit Realism / Imported data sheets in Excel, save, then call this
    function.

    Args:
        path: Path to the LIC-DSF Excel workbook.

    Returns:
        `RealismLoad` with imported catalog, capital, multipliers, LIC
        program histogram, and invest-growth series.
    """
    return RealismLoad(
        imported=load_imported_data(path),
        capital=load_capital_assumptions(path),
        multipliers=load_multiplier_grid(path),
        lic_programs=load_lic_program_distribution(path),
        invest_growth=load_invest_growth_series(path),
    )


def load_probability(path: str | Path) -> DistressCovariates:
    """Load Probability-approach distress covariates from the workbook.

    Edit Input 3 / Imported-data probability cells in Excel, save, then call
    this function.

    Args:
        path: Path to the LIC-DSF Excel workbook.

    Returns:
        `DistressCovariates` for Output 6 probability panels.
    """
    return load_distress_covariates(path)
