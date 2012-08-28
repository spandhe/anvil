# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Based off of http://www.brianlane.com/nice-changelog-entries.html
#
# git-changelog - Output a rpm changelog
#
# Copyright (C) 2009-2010  Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: David Cantrell <dcantrell@redhat.com>
# Author: Brian C. Lane <bcl@redhat.com>

import iso8601
import textwrap

from anvil import shell as sh


class RpmChangeLog(object):
    def __init__(self, wkdir, max_history=100):
        self.wkdir = wkdir
        self.max_history = max_history
        self.date_buckets = None

    def _getCommitDetail(self, commit, field):
        detail_cmd = ['git', 'log', '-1', "--pretty=format:%s" % field, commit]
        (stdout, stderr) = sh.execute(*detail_cmd, cwd=self.wkdir)
        ret = stdout.strip('\n').splitlines()
        if len(ret) == 1:
            ret = ret[0]
        else:
            ret = filter(lambda x: x != '', ret)
        return ret

    def _filter_logs(self, line):
        if not line.strip():
            return False
        if (line.find('l10n: ') != 41 and line.find('Merge commit') != 41 and line.find('Merge branch') != 41):
            return True
        return False

    def _getLog(self):
        log_cmd = ['git', 'log', '--pretty=oneline', '-n%s' % (self.max_history)]
        (sysout, stderr) = sh.execute(*log_cmd, cwd=self.wkdir)
        lines = filter(self._filter_logs, sysout.strip('\n').splitlines())

        # Extract the raw commit details
        log = []
        for line in lines:
            fields = line.split(' ')
            commit = fields[0]

            # http://opensource.apple.com/source/Git/Git-26/src/git-htmldocs/pretty-formats.txt
            summary = self._getCommitDetail(commit, "%s")
            date = self._getCommitDetail(commit, "%ai")
            author_email = self._getCommitDetail(commit, "%aE")
            author_name = self._getCommitDetail(commit, "%an")
            log.append({
                'summary': summary,
                'when': iso8601.parse_date(date),
                'author_email': author_email,
                'author_name': author_name,
            })
        
        # Bucketize the dates
        date_buckets = {}
        for entry in log:
            day = entry['when'].date()
            if day in date_buckets:
                date_buckets[day].append(entry)
            else:
                date_buckets[day] = [entry]
        return date_buckets

    def formatLog(self):
        if self.date_buckets is None:
            self.date_buckets = self._getLog()
        date_buckets = self.date_buckets
        lines = []
        dates = date_buckets.keys()
        for d in reversed(sorted(dates)):
            summaries = date_buckets[d]
            for msg in summaries:
                header = "* %s %s <%s>" % (d.strftime("%a %b %d %Y"),
                                           msg['author_name'], msg['author_email'])
                lines.append(header)
                summary = msg['summary']
                sublines = textwrap.wrap(summary, 77)
                lines.append("- %s" % sublines[0])
                if len(sublines) > 1:
                    for subline in sublines[1:]:
                        lines.append("  %s" % subline)
        # Replace utf8 with ? just incase
        contents = "\n".join(lines)
        contents = contents.decode('utf8').encode('ascii', 'replace')
        return contents