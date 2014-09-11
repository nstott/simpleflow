import inspect
from importlib import import_module

from cdf.log import logger
import cdf.features
from cdf.core.streams.base import StreamDefBase


class Feature(object):

    @classmethod
    def get_features(cls,):
        if hasattr(cls, 'FEATURES'):
            return cls.FEATURES

        cls.FEATURES = []

        for name, module in (
                (name, module) for name, module in
                inspect.getmembers(cdf.features, inspect.ismodule)):
            settings = __import__(
                '.'.join([cdf.features.__name__, name, 'settings']),
                fromlist=['*'])
            feature = Feature(
                identifier=name,
                name=getattr(settings, "NAME", None),
                description=getattr(settings, "DESCRIPTION", None),
                groups=getattr(settings, "GROUPS", []),
                order=getattr(settings, "ORDER", None)
            )
            cls.FEATURES.append(feature)
        # Sort features by order
        cls.FEATURES = sorted(cls.FEATURES, key=lambda f: f.order)
        return cls.FEATURES

    def __init__(self, identifier, name, description, groups, order=None):
        """
        :param identifier : Identifier of the feature (ex : amin)
        :param name: Verbose name of the feature
        :param description : Description of the feature
        :param groups : a list of dict. ex : [{"id": "metrics", "name": "Main metrics"}, ..]
        :param priority : Worth of the feature (smaller is better).
                          When generating concatenated groups/fields from a crawl,
                          it will iterate on features sorted by priority
        """
        self.identifier = identifier
        self.name = name
        self.description = description
        self.groups = groups
        self.order = order

    def __unicode__(self):
        return unicode(self.identifier)

    def get_streams_def(self):
        """
        Return streams definition from the current feature
        """
        obj = []
        streams = import_module('cdf.features.{}.streams'.format(self.identifier))
        methods = inspect.getmembers(streams, predicate=inspect.isclass)
        for method_name, klass in methods:
            if issubclass(klass, StreamDefBase) and klass != StreamDefBase:
                obj.append(klass())
        return obj

    def get_streams_def_processing_document(self):
        """
        Return all streams needed to compute urls documents
        """
        obj = []
        for s in self.get_streams_def():
            if hasattr(s, 'process_document'):
                obj.append(s)
        return obj

    def get_insights(self):
        """Return the list of insights associated with the feature.
        The insights of feature x are expected to be stored in
        cdf.features.x.insights.insights
        If such a list does not exist, the method returns an empty list.
        :returns: list
        """
        insights_module_name = '.'.join(
            [cdf.features.__name__, self.identifier, 'insights']
        )
        try:
            insights_module = import_module(insights_module_name)
        except ImportError:
            logger.warning("Could not find insights for feature '%s'. Does '%s' exists?",
                           self.identifier,
                           insights_module_name)
            return []

        if hasattr(insights_module, "insights"):
            return insights_module.insights
        else:
            logger.warning("Could not find an element named insights in '%s'.",
                           insights_module_name)
            return []


