# -*- coding: utf-8 -*-

#CODE Reference taken from GNU HEALTH for disease and category.
{
    'name' : 'International Classification of Diseases (ICD10)',
    'summary': 'International Classification of Diseases and Diseases Category (ICD10).',
    'version': '1.0.1',
    'category': 'Medical',
    'license': 'OPL-1',
    'depends' : ['yan_hims_tasks'],
    'author': 'Yanos Group',
    'website': 'www.yanosgroup.com',
    'description': """
        International Classification of Diseases, icd10 for hospital Information management system
    """,
    "data": [
        "data/disease_categories.xml",
        "data/diseases.xml",
    ],
    "cloc_exclude": [
        "data/*.xml",
    ],
    'installable': True,
    'application': False,
    'sequence': 2,

}
