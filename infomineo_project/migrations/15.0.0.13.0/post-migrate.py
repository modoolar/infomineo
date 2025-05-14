# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import logging


def migrate(cr, version):
    """"""
    logger = logging.getLogger(__name__)
    logger.info("Post-migrate 15.0.0.13.0 started")

    cr.execute(
        """
            do
            $$
            declare
                project record;
                task record;
                lob_field record;
                seq_name varchar;
                current_seq_no integer;
                lob_name varchar;
                lob_abbrev varchar;
                part text;
            begin
                FOR project in SELECT
                                    p.id, p.name
                                FROM
                                    project_project p
                                WHERE p.active = True
                LOOP
                    seq_name := 'project_project_next_task_code_seq_' || project.id::varchar(255);

                    EXECUTE 'DROP SEQUENCE IF EXISTS ' || seq_name|| ';';
                    EXECUTE 'CREATE SEQUENCE ' || seq_name || ' START WITH 1 MAXVALUE 999999;';

                    FOR task in SELECT
                                    pt.id, pt.name, pt.project_id, pt.line_of_business
                                    from project_task pt
                                WHERE
                                    pt.active = True AND pt.project_id = project.id
                    LOOP
                        current_seq_no := nextval(seq_name);
                        SELECT
                            mfs.name INTO lob_name
                        FROM
                            ir_model_fields_selection mfs
                        WHERE
                            mfs.field_id = (
                                SELECT
                                    mf.id
                                FROM
                                    ir_model_fields mf
                                WHERE
                                    mf.name = 'line_of_business' and mf.model = 'project.task'
                            ) AND mfs.value = task.line_of_business;

                        lob_abbrev := '';
                        FOREACH part in array string_to_array(lob_name, ' ')
                            LOOP
                                lob_abbrev := lob_abbrev || upper(substring(part from 1 for 1));
                            END LOOP;

                        UPDATE
                            project_task pt
                        SET
                            code = lob_abbrev || '/' || project.name || '/' || current_seq_no::varchar,
                            current_task_number = current_seq_no
                        WHERE pt.id = task.id;

                    END LOOP;

                    EXECUTE 'UPDATE project_project pp set next_task_number = '|| current_seq_no + 1 ||' WHERE pp.id = ' ||  project.id || ';';
                    EXECUTE 'DROP SEQUENCE ' || seq_name || ';';

                END LOOP;
            END;
            $$;
        """
    )

    logger.info("Post-migrate 15.0.0.13.0 finished")
