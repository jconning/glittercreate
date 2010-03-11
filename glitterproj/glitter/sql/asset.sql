# Need to remove the not null constraint that syncdb added
alter table glitter_asset modify last_added_to_repo_date datetime;
