import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from fetlab.physics import mos_cv, mosfet_id, subthreshold_slope_mvdec, dibl_model
from fetlab.scaling import moore_doubling_years, dennard_scale

def test_cv_accumulation():
    assert abs(mos_cv(-2, 2e-9, 1e16, -0.9, True)/ (3.9*8.854187817e-12/2e-9) - 1.0) < 1e-9

def test_iv_degraded_less():
    W,L=1e-6,0.5e-6
    a=mosfet_id(1.8,1.5,W,L,2e-9,1e16,theta_per_v=0.0,esat_vcm=1e9)
    b=mosfet_id(1.8,1.5,W,L,2e-9,1e16,theta_per_v=0.5,esat_vcm=4e4)
    assert b < a

def test_moore_range():
    assert 1.5 < moore_doubling_years() < 3.0

def test_dibl_anchors():
    assert 25 < dibl_model(12e-9,6e-9) < 40
    assert 65 < dibl_model(10e-9,6e-9) < 90

def test_ss():
    assert 60 < subthreshold_slope_mvdec(1.25) < 110
