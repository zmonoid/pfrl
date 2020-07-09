import torch
from torch import distributions as dists
from torch.distributions.utils import _sum_rightmost


def _sample_with_log_prob_transform(distrib, use_rsample=False):
    assert len(distrib.transforms) == 1
    base_dist = distrib.base_dist
    x = base_dist.rsample() if use_rsample else base_dist.sample()
    base_log_prob = base_dist.log_prob(x)
    y = distrib.transforms[0](x)
    log_probs = base_log_prob - distrib.transforms[0].log_abs_det_jacobian(x, y)
    return y, torch.sum(log_probs, dim=len(log_probs.shape) - 1)


def sample_with_log_prob(distrib, use_rsample=False):
    assert isinstance(distrib, dists.Distribution)
    if isinstance(distrib, dists.Independent):
        sample, log_prob = sample_with_log_prob(distrib.base_dist)
        return sample, _sum_rightmost(log_prob, distrib.reinterpreted_batch_ndims)
    if isinstance(distrib, dists.transformed_distribution.TransformedDistribution):
        assert len(distrib.transforms) == 1
        if distrib.transforms[0].bijective:
            return _sample_with_log_prob_transform(distrib, use_rsample)
    sample = distrib.rsample() if use_rsample else distrib.sample()
    return sample, distrib.log_prob(sample)