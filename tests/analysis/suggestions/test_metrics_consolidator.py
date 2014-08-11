import unittest

from cdf.analysis.suggestions.aggregator import MetricsConsolidator


class TestMetricsConsolidator(unittest.TestCase):

    def test_simple(self):
        stats_part_0 = [
            {
                "cross_properties": ["www.site.com", "homepage", "text/html", 0, 200, True, True],
                "counters": {
                    "pages_nb": 10,
                }
            },
            {
                "cross_properties": ["my.site.com", "product", "text/html", 0, 301, True, True],
                "counters": {
                    "pages_nb": 30,
                }
            },
            {
                "cross_properties": ["my.site.com", "product", "text/html", 0, 200, True, True],
                "counters": {
                    "pages_nb": 10,
                    "inlinks_internal_nb": {
                        "total": 1,
                        "nofollow": 1,
                        "follow": 0,
                        "nofollow_combinations": {
                            "link_meta": 1
                        }
                    }
                }
            }
        ]

        stats_part_1 = [
            {
                "cross_properties": ["my.site.com", "product", "text/html", 0, 200, True, True],
                "counters": {
                    "pages_nb": 12,
                    "inlinks_internal_nb": {
                        "total": 11,
                        "nofollow": 11,
                        "follow": 0,
                        "nofollow_combinations": {
                            "link_meta": 1,
                            "link": 10
                        }
                    }
                }
            },
            {
                "cross_properties": ["music.site.com", "artist", "text/html", 0, 404, True, True],
                "counters": {
                    "pages_nb": 30,
                }
            }
        ]

        stats_part_2 = [
            {
                "cross_properties": ["music.site.com", "artist", "text/html", 0, 200, True, True],
                "counters": {
                    "pages_nb": 130,
                }
            }
        ]

        metadata_only_part = [
            {
                "cross_properties": ['music.site.com', 'artist', 'text/html', 0, 200, True, True],
                "counters": {
                    "metadata_nb": {
                        "h1": {
                            "filled": 100,
                            "unique": 90
                        }
                    }
                }
            },
            {
                "cross_properties": ['music.site.com', 'artist', 'text/html', 0, 404, True, True],
                "counters": {
                    "metadata_nb": {
                        "title": 20,
                        "unique": 20
                    }
                }
            },
        ]

        c = MetricsConsolidator([stats_part_0, stats_part_1, stats_part_2, metadata_only_part])
        aggregated_data = c.consolidate(return_flatten=False)

        expected_data = {
            ('music.site.com', 'artist', 'text/html', 0, 200, True, True): {
                'pages_nb': 130,
                'metadata_nb': {
                    'h1': {
                        'filled': 100,
                        'unique': 90
                    }
                }
            },
            ('music.site.com', 'artist', 'text/html', 0, 404, True, True): {
                'pages_nb': 30,
                "metadata_nb": {
                    "title": 20,
                    "unique": 20
                }
            },
            ('www.site.com', 'homepage', 'text/html', 0, 200, True, True): {
                'pages_nb': 10,
            },
            ('my.site.com', 'product', 'text/html', 0, 200, True, True): {
                'pages_nb': 22,
                "inlinks_internal_nb": {
                    "total": 12,
                    "nofollow": 12,
                    "follow": 0,
                    "nofollow_combinations": {
                        "link_meta": 2,
                        "link": 10
                    }
                }
            },
            ('my.site.com', 'product', 'text/html', 0, 301, True, True): {
                'pages_nb': 30,
            }
        }

        for key, value in expected_data.iteritems():
            self.assertEquals(aggregated_data[key], value)