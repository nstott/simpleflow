from collections import Counter
from itertools import groupby

from cdf.features.main.streams import InfosStreamDef
from cdf.features.links.streams import OutlinksStreamDef, BadLinksStreamDef


def get_bad_links(stream_infos, stream_outlinks):
    """
    (url_src_id, url_dest_id, error_http_code)
    """
    # Resolve indexes
    http_code_idx = InfosStreamDef.field_idx('http_code')
    url_id_idx = InfosStreamDef.field_idx('id')
    dest_url_idx = OutlinksStreamDef.field_idx('dst_url_id')
    src_url_idx = OutlinksStreamDef.field_idx('id')
    link_type_idx = OutlinksStreamDef.field_idx('link_type')

    # Find all bad code pages
    # (url_id -> error_http_code)
    bad_code = {}
    for info in stream_infos:
        http_code = info[http_code_idx]
        if (http_code >= 300):
            bad_code[info[url_id_idx]] = http_code

    # Iterator over outlinks and extract all normal links whose destination
    # is in the *bad_code* dict
    for outlink in stream_outlinks:
        dest = outlink[dest_url_idx]
        link_type = outlink[link_type_idx]
        if link_type == 'a' and dest in bad_code:
            yield (outlink[src_url_idx], dest, bad_code[dest])


def get_bad_link_counters(stream_bad_links):
    """
    A counter of (url_src_id, error_http_code, count)
    Sorted on `url_src_id`
    """
    # Resolve indexes
    src_url_idx = BadLinksStreamDef.field_idx('id')
    http_code_idx = BadLinksStreamDef.field_idx('http_code')

    # Group by source url_id
    for src_url_id, g in groupby(stream_bad_links, lambda x: x[src_url_idx]):
        links = list(g)
        cnt = Counter()

        for link in links:
            cnt[link[http_code_idx]] += 1

        for http_code in cnt:
            yield (src_url_id, http_code, cnt[http_code])
