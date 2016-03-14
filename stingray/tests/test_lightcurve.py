import warnings
import numpy as np
import warnings
from nose.tools import raises
from stingray import Lightcurve

np.random.seed(20150907)


class TestLightcurve(object):

    @classmethod
    def setup_class(cls):
        cls.times = [1, 2, 3, 4]
        cls.counts = [2, 2, 2, 2]
        cls.dt = 1.0

    def test_create(self):
        """
        Demonstrate that we can create a trivial Lightcurve object.
        """
        lc = Lightcurve(self.times, self.counts)

    def test_irregular_time_warning(self):
        """
        Check if inputting an irregularly spaced time iterable throws out
        a warning.
        """
        times = [1, 2, 3, 5, 6]
        counts = [2, 2, 2, 2, 2]
        warn_str = ("SIMON says: Bin sizes in input time array aren't equal "
                    "throughout! This could cause problems with Fourier "
                    "transforms. Please make the input time evenly sampled.")

        with warnings.catch_warnings(record=True) as w:
            lc = Lightcurve(times, counts)
            assert str(w[0].message) == warn_str

    def test_lightcurve_from_toa(self):
        lc = Lightcurve.make_lightcurve(self.times, self.dt)

    def test_tstart(self):
        tstart = 0.0
        lc = Lightcurve.make_lightcurve(self.times, self.dt, tstart=0.0)
        assert lc.tstart == tstart
        assert lc.time[0] == tstart + 0.5*self.dt

    def test_tseg(self):
        tstart = 0.0
        tseg = 5.0
        lc = Lightcurve.make_lightcurve(self.times, self.dt,
                                        tseg=tseg, tstart=tstart)

        assert lc.tseg == tseg
        assert lc.time[-1] - lc.time[0] == tseg - self.dt

    def test_nondivisble_tseg(self):
        """
        If the light curve length input is not divisible by the time
        resolution, the last (fractional) time bin will be dropped.
        """
        tstart = 0.0
        tseg = 5.5
        lc = Lightcurve.make_lightcurve(self.times, self.dt,
                                        tseg=tseg, tstart=tstart)
        assert lc.tseg == int(tseg/self.dt)

    def test_correct_timeresolution(self):
        lc = Lightcurve.make_lightcurve(self.times, self.dt)
        assert np.isclose(lc.dt, self.dt)

    def test_bin_correctly(self):
        ncounts = np.array([2, 1, 0, 3])
        tstart = 0.0
        tseg = 4.0

        toa = np.hstack([np.random.uniform(i, i+1, size=n)
                         for i, n in enumerate(ncounts)])

        dt = 1.0
        lc = Lightcurve.make_lightcurve(toa, dt, tseg=tseg, tstart=tstart)

        assert np.allclose(lc.counts, ncounts)

    def test_countrate(self):
        dt = 0.5
        mean_counts = 2.0
        times = np.arange(0 + dt/2, 5 - dt/2, dt)
        counts = np.zeros_like(times) + mean_counts
        lc = Lightcurve(times, counts)
        assert np.allclose(lc.countrate, np.zeros_like(counts) +
                           mean_counts/dt)

    def test_input_countrate(self):
        dt = 0.5
        mean_counts = 2.0
        times = np.arange(0 + dt/2, 5 - dt/2, dt)
        countrate = np.zeros_like(times) + mean_counts
        lc = Lightcurve(times, countrate, input_counts=False)
        assert np.allclose(lc.counts, np.zeros_like(countrate) +
                           mean_counts*dt)

    @raises(TypeError)
    def test_init_with_none_data(self):
        dt = 0.5
        mean_counts = 2.0
        times = np.arange(0 + dt/2, 5 - dt/2, dt)
        counts = np.array([None for i in range(times.shape[0])])
        lc = Lightcurve(times, counts)

    @raises(AssertionError)
    def test_init_with_inf_data(self):
        dt = 0.5
        mean_counts = 2.0
        times = np.arange(0 + dt/2, 5 - dt/2, dt)
        counts = np.array([np.inf for i in range(times.shape[0])])
        lc = Lightcurve(times, counts)

    @raises(AssertionError)
    def test_init_with_nan_data(self):
        dt = 0.5
        mean_counts = 2.0
        times = np.arange(0 + dt/2, 5 - dt/2, dt)
        counts = np.array([np.nan for i in range(times.shape[0])])
        lc = Lightcurve(times, counts)

    @raises(AssertionError)
    def test_add_with_different_time_arrays(self):
        _times = [1, 2, 3, 4, 5]
        _counts = [2, 2, 2, 2, 2]

        lc1 = Lightcurve(self.times, self.counts)
        lc2 = Lightcurve(_times, _counts)

        lc = lc1 + lc2

    @raises(AssertionError)
    def test_add_with_unequal_time_arrays(self):
        _times = [1, 3, 5, 7]

        lc1 = Lightcurve(self.times, self.counts)
        lc2 = Lightcurve(_times, self.counts)

        lc = lc1 + lc2

    def test_add_with_equal_time_arrays(self):
        _counts = [1, 1, 1, 1]

        lc1 = Lightcurve(self.times, self.counts)
        lc2 = Lightcurve(self.times, _counts)

        lc = lc1 + lc2

        assert np.all(lc.counts == lc1.counts + lc2.counts)
        assert np.all(lc.countrate == lc1.countrate + lc2.countrate)

    def test_join_with_different_dt(self):
        _times = [5, 5.5, 6]
        _counts = [2, 2, 2]

        lc1 = Lightcurve(self.times, self.counts)
        lc2 = Lightcurve(_times, _counts)

        with warnings.catch_warnings(record=True) as w:
            lc1.join(lc2)
            print(w)
            assert "both the lightcurves are not same" in str(w[0].message)

    def test_join_disjoint_time_arrays(self):
        _times = [5, 6, 7, 8]
        _counts = [2, 2, 2, 2]

        lc1 = Lightcurve(self.times, self.counts)
        lc2 = Lightcurve(_times, _counts)

        lc = lc1.join(lc2)

        assert len(lc.counts) == len(lc.time) == 8
        assert np.all(lc.counts == 2)

    def test_join_merged_time_arrays(self):
        _times = [3, 4, 5, 6]
        _counts = [2, 2, 2, 2]

        lc1 = Lightcurve(self.times, self.counts)
        lc2 = Lightcurve(_times, _counts)

        lc = lc1.join(lc2)

        assert len(lc.counts) == len(lc.time) == 6
        assert len(np.where(lc.counts==4)[0]) == 2
        assert len(np.where(lc.counts==2)[0]) == 4

    def test_join_equal_arrays(self):
        """
        ``lc.join()`` should work like ``lc.__add__()`` if the time
        arrays are equal.
        """
        lc1 = Lightcurve(self.times, self.counts)
        lc2 = Lightcurve(self.times, self.counts)

        assert np.all(lc1.join(lc2).counts == (lc1 + lc2).counts)
        assert np.all(lc1.join(lc2).time == (lc1 + lc2).time)

class TestLightcurveRebin(object):

    @classmethod
    def setup_class(cls):
        dt = 0.0001220703125
        n = 1384132
        mean_counts = 2.0
        times = np.arange(dt/2, dt/2 + n*dt, dt)
        counts = np.zeros_like(times) + mean_counts
        cls.lc = Lightcurve(times, counts)

    def test_rebin_even(self):
        dt_new = 2.0
        lc_binned = self.lc.rebin_lightcurve(dt_new)
        assert np.isclose(lc_binned.dt, dt_new)
        counts_test = np.zeros_like(lc_binned.time) + \
            self.lc.counts[0]*dt_new/self.lc.dt
        assert np.allclose(lc_binned.counts, counts_test)

    def test_rebin_odd(self):
        dt_new = 1.5
        lc_binned = self.lc.rebin_lightcurve(dt_new)
        assert np.isclose(lc_binned.dt, dt_new)

        counts_test = np.zeros_like(lc_binned.time) + \
            self.lc.counts[0]*dt_new/self.lc.dt
        assert np.allclose(lc_binned.counts, counts_test)

    def rebin_several(self, dt):
        """
        TODO: Not sure how to write tests for the rebin method!
        """
        lc_binned = self.lc.rebin_lightcurve(dt)
        assert len(lc_binned.time) == len(lc_binned.counts)

    def test_rebin_equal_numbers(self):
        dt_all = [2, 3, np.pi, 5]
        for dt in dt_all:
            yield self.rebin_several, dt
