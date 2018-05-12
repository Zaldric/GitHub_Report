#!/usr/bin/env python3
import sys
import json
import requests
import datetime

if __name__ == '__main__':
    if len(sys.argv) > 1:
        bad_references = list()
        good_references = list()

        for reference in sys.argv[1:]:
            if '/' not in reference:
                bad_references.append(reference)
            else:
                good_references.append(reference)

        if not bad_references:
            issues = list()
            non_exists = list()
            exists = list()
            day_occurrences = dict()

            for reference in sys.argv[1:]:
                params = str(reference).split('/')
                url = 'https://api.github.com/repos/' + params[0] + '/' + params[1] + '/issues'
                response = requests.get(url)

                if response:
                    have_issue = False
                    for json_data in json.loads(response.text):
                        repository_data = dict()
                        repository_data['id'] = json_data['id']
                        repository_data['state'] = json_data['state']
                        repository_data['title'] = json_data['title']
                        repository_data['repository'] = reference
                        repository_data['created_at'] = json_data['created_at']
                        issues.append(repository_data)
                        day = str(json_data['created_at']).split('T')[0]
                        have_issue = True

                        if day not in day_occurrences:
                            day_occurrences[day] = dict(zip(good_references, [0] * len(good_references)))
                            day_occurrences[day]['total'] = 0
                        if reference in day_occurrences[day]:
                            day_occurrences[day][reference] += 1
                            day_occurrences[day]['total'] += 1

                    if not have_issue:
                        exists.append(reference)
                else:
                    non_exists.append(reference)

            if non_exists:
                print("The following references don't exist in GitHub and couldn't be processed: " + ', '.join(
                    non_exists))

            if exists:
                print("The following references don't have any issue: " + ', '.join(exists))

            if issues:
                issues.sort(key=lambda x: datetime.datetime.strptime(x['created_at'], '%Y-%m-%dT%H:%M:%SZ'))
                day = sorted(day_occurrences, key=lambda k: day_occurrences[k]['total'])[1:]
                max_frequency = \
                day_occurrences[max(day_occurrences.keys(), key=(lambda k: day_occurrences[k]['total']))]['total']
                top_day = list()

                for day, occurrences in day_occurrences.items():
                    if occurrences['total'] == max_frequency:
                        top_day.append(day)

                top_day.sort(key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
                top_day_info = dict()
                top_day_info['top_day'] = top_day[len(top_day) - 1]
                top_day_info['ocurrences'] = day_occurrences[top_day[len(top_day) - 1]]
                issues_dict = dict()
                issues_dict['issues'] = issues

                json_string_issues = json.dumps(issues_dict)
                print(json_string_issues, 'issues')
                json_string_top_day = json.dumps(top_day_info)
                print(json_string_top_day)
                exit(0)
            else:
                exit(0) if exists else exit(1)
        else:
            print(
                "Error: the following references don't match the format owner/repository: " + ', '.join(bad_references))
            exit(1)
    else:
        print('Usage: github_report.py [owner/repository ...]')
        exit(1)
