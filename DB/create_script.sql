BEGIN;

-- ========== DROP FUNCTIONS ==========
DROP FUNCTION IF EXISTS public.get_meeting_json(integer) CASCADE;
DROP FUNCTION IF EXISTS public.insert_meeting(date, text, text) CASCADE;
DROP FUNCTION IF EXISTS public.attach_document(integer, text, bytea) CASCADE;
DROP FUNCTION IF EXISTS public.ensure_document_type(text) CASCADE;
DROP FUNCTION IF EXISTS public.add_agenda_item(integer, text, text, integer, text, integer) CASCADE;
DROP FUNCTION IF EXISTS public.get_meetings_json() CASCADE;

-- ========== DROP TABLES ==========
DROP TABLE IF EXISTS public."Documents" CASCADE;
DROP TABLE IF EXISTS public."DocumentDatas" CASCADE;
DROP TABLE IF EXISTS public."DocumentTypes" CASCADE;
DROP TABLE IF EXISTS public."AgendaItems" CASCADE;
DROP TABLE IF EXISTS public."Summaries" CASCADE;
DROP TABLE IF EXISTS public."Meetings" CASCADE;

-- ========== TABLES ==========

CREATE TABLE public."Meetings" (
    "MeetingID" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "Date" date NOT NULL,
    "VideoURL" text NOT NULL,
    "Title" text NOT NULL
);

CREATE TABLE public."AgendaItems" (
    "AgendaItemID" bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "MeetingID" integer NOT NULL REFERENCES public."Meetings"("MeetingID") ON UPDATE CASCADE ON DELETE CASCADE,
    "Title" text NOT NULL,
    "Description" text NOT NULL,
    "ItemNumber" integer NOT NULL,
    "OrderNumber" integer NOT NULL,
    "FileNumber" text
);

CREATE TABLE public."Summaries" (
    "SummaryId" bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "MeetingID" integer NOT NULL REFERENCES public."Meetings"("MeetingID") ON UPDATE CASCADE ON DELETE CASCADE,
    "Title" text NOT NULL,
    "Summary" text NOT NULL,
    "StartTime" text NOT NULL
);

CREATE TABLE public."DocumentTypes" (
    "DocumentTypeID" smallint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "Name" text NOT NULL UNIQUE
);

CREATE TABLE public."DocumentDatas" (
    "DocumentDataID" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "DocumentTypeID" smallint NOT NULL REFERENCES public."DocumentTypes"("DocumentTypeID") ON UPDATE CASCADE ON DELETE CASCADE,
    "Data" bytea NOT NULL
);

CREATE TABLE public."Documents" (
    "DocumentID" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "MeetingID" integer NOT NULL REFERENCES public."Meetings"("MeetingID") ON UPDATE CASCADE ON DELETE CASCADE,
    "DocumentDataID" integer NOT NULL REFERENCES public."DocumentDatas"("DocumentDataID") ON UPDATE CASCADE ON DELETE CASCADE
);

-- ========== FUNCTIONS ==========

CREATE FUNCTION public.ensure_document_type(p_name text) RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE id int;
BEGIN
  INSERT INTO "DocumentTypes"("Name") VALUES (p_name)
  ON CONFLICT ("Name") DO NOTHING;
  SELECT "DocumentTypeID" INTO id FROM "DocumentTypes" WHERE "Name" = p_name;
  RETURN id;
END$$;

COMMENT ON FUNCTION public.ensure_document_type(p_name text)
IS 'Upsert by name; return id';

CREATE FUNCTION public.add_agenda_item(
  p_meeting_id integer,
  p_title text,
  p_description text,
  p_item_number integer,
  p_file_number text,
  p_order integer
) RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE new_id bigint; v_order int;
BEGIN
  v_order := COALESCE(
    p_order,
    (SELECT COALESCE(MAX("OrderNumber"), 0) + 1
     FROM "AgendaItems"
     WHERE "MeetingID" = p_meeting_id)
  );

  INSERT INTO "AgendaItems"(
    "MeetingID", "Title", "Description", "ItemNumber", "OrderNumber", "FileNumber"
  )
  VALUES (
    p_meeting_id, p_title, p_description, p_item_number, v_order, p_file_number
  )
  RETURNING "AgendaItemID" INTO new_id;

  RETURN new_id;
END$$;

CREATE FUNCTION public.attach_document(p_meeting_id integer, p_document_type_name text, p_data bytea)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE type_id int; data_id int; doc_id int;
BEGIN
  type_id := ensure_document_type(p_document_type_name);

  INSERT INTO "DocumentDatas"("DocumentTypeID","Data")
  VALUES (type_id, p_data)
  RETURNING "DocumentDataID" INTO data_id;

  INSERT INTO "Documents"("MeetingID","DocumentDataID")
  VALUES (p_meeting_id, data_id)
  RETURNING "DocumentID" INTO doc_id;

  RETURN doc_id;
END$$;

CREATE FUNCTION public.insert_meeting(p_date date, p_videourl text, p_title text)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE new_id integer;
BEGIN
  INSERT INTO "Meetings" ("Date", "VideoURL", "Title")
  VALUES (p_date, p_videourl, p_title)
  RETURNING "MeetingID" INTO new_id;
  RETURN new_id;
END;$$;

CREATE FUNCTION public.get_meetings_json()
RETURNS jsonb
LANGUAGE sql
STABLE
AS $$
SELECT jsonb_agg(to_jsonb(m) ORDER BY m."Date" DESC, m."MeetingID" DESC)
FROM public."Meetings" m;
$$;

CREATE FUNCTION public.get_meeting_json(p_meeting_id integer)
RETURNS jsonb
LANGUAGE sql
AS $$
SELECT jsonb_build_object(
  'meeting', to_jsonb(m),
  'agenda', (SELECT jsonb_agg(to_jsonb(a) ORDER BY "OrderNumber")
             FROM "AgendaItems" a WHERE a."MeetingID" = m."MeetingID"),
  'summaries', (SELECT jsonb_agg(to_jsonb(s))
             FROM "Summaries" s WHERE s."MeetingID" = m."MeetingID"),
  'documents', (
    SELECT jsonb_agg(jsonb_build_object(
      'documentId', d."DocumentID",
      'dataId', dd."DocumentDataID",
      'type', dt."Name"
    ))
    FROM "Documents" d
    JOIN "DocumentDatas" dd ON dd."DocumentDataID" = d."DocumentDataID"
    JOIN "DocumentTypes" dt ON dt."DocumentTypeID" = dd."DocumentTypeID"
    WHERE d."MeetingID" = m."MeetingID")
)
FROM "Meetings" m WHERE m."MeetingID" = p_meeting_id;
$$;

-- ========== SEQUENCE RESET ==========
-- Identity sequences are created automatically; these set them to start at 1.
SELECT pg_catalog.setval('public."Meetings_MeetingID_seq"', 1, true);
SELECT pg_catalog.setval('public."AgendaItems_AgendaItemID_seq"', 1, false);
SELECT pg_catalog.setval('public."DocumentDatas_DocumentDataID_seq"', 1, false);
SELECT pg_catalog.setval('public."DocumentTypes_DocumentTypeID_seq"', 1, false);
SELECT pg_catalog.setval('public."Documents_DocumentID_seq"', 1, false);

COMMIT;

BEGIN;

-- Insert meetings (ID will auto-generate)
INSERT INTO public."Meetings" ("Date","VideoURL","Title") VALUES
  ('2025-09-09','https://youtube.com/watch?v=V-6JeJxgoEw','City Council Meeting'),
  ('2025-09-10','https://youtube.com/watch?v=BazoAgcwpH0','City Council Meeting'),
  ('2025-09-12','https://youtube.com/watch?v=BKg6FTrMvwE','City Council Meeting');

-- Insert agenda items for Sep 09, 2025
WITH m AS (
  SELECT "MeetingID" AS mid FROM public."Meetings" WHERE "Date" = '2025-09-09'
),
src AS (
  SELECT
    (j->>'item_number')::int            AS item_number,
    j->>'file_number'                   AS file_number,
    j->>'title'                         AS title,
    COALESCE(j->>'description','')      AS description
  FROM jsonb_array_elements(
    $$ [
    {
        "item_number": "1",
        "file_number": "25-0160-S70",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 1717 West 6th Street.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 1717 West 6th Street. (Lien: $2,624.54)"
    },
    {
        "item_number": "2",
        "file_number": "14-0160-S418",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 1546 West 7th Street.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 1546 West 7th Street. (Lien: $1,483.26)"
    },
    {
        "item_number": "3",
        "file_number": "25-0160-S69",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 5534 North Cantaloupe Avenue.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 5534 North Cantaloupe Avenue. (Lien: $1,276.56)"
    },
    {
        "item_number": "4",
        "file_number": "25-0160-S83",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 6803 North Aldea Avenue.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 6803 North Aldea Avenue. (Lien: $2,644.84)"
    },
    {
        "item_number": "5",
        "file_number": "25-0160-S103",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 7708 North Beck Avenue.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 7708 North Beck Avenue. (Lien: $1,276.56)"
    },
    {
        "item_number": "6",
        "file_number": "14-0160-S447",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 11366 North Oro Vista Avenue.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 11366 North Oro Vista Avenue. (Lien: $2,604.55)"
    },
    {
        "item_number": "7",
        "file_number": "16-0160-S284",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 1541 West Florence Avenue.",
        "description": "Recommendation for Council action: PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 1541 West Florence Avenue. (Lien: $4,547.58)"
    },
    {
        "item_number": "8",
        "file_number": "25-0160-S72",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 572 East M Street.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 572 East M Street."
    },
    {
        "item_number": "9",
        "file_number": "15-0989-S44",
        "title": "AD HOC COMMITTEE ON THE 2028 OLYMPICS AND PARALYMPIC GAMES REPORT relative to the Second Amendment to the Venue Plan for the 2028 Olympic and Paralympic Games.",
        "description": "Recommendations for Council action: 1. APPROVE the Second Amendment to the Venue Plan for the 2028 Olympic and Paralympic Games, in accordance with Section 6.6 of the Games Agreement, to authorize the relocation of the Aquatics Diving sports discipline from a venue in the City of Los Angeles to a venue in the City of Pasadena, California, contingent upon completion of a signed definitive agreement between the Los Angeles Organizing Committee for the Olympic and Paralympic Games 2028 (LA28) and the Department of Recreation and Parks (RAP) regarding the licensing and right to access the John C. Argue Swim Stadium at Exposition Park and a commitment by LA 28 to undertake efforts to bring it to national and international competition standards in order to create a lasting community benefit. 2. INSTRUCT the RAP, and REQUEST LA28, to report to Council on the definitive agreement regarding the licensing and right to access the John C. Argue Swim Stadium at Exposition Park and the commitment by LA28 to undertake efforts to bring it to national and international competition standards in order to create a lasting community benefit. Fiscal Impact Statement: The Chief Legislative Analyst and City Administrative Officer report that there is no fiscal impact resulting from the recommendations in the report. Community Impact Statement: None Submitted"
    },
    {
        "item_number": "10",
        "file_number": "15-0989-S51",
        "title": "AD HOC COMMITTEE ON THE 2028 OLYMPICS AND PARALYMPIC GAMES REPORT relative to the LA28 Impact and Sustainability Plan for the 2028 Olympic and Paralympic Games.",
        "description": "Recommendations for Council action: 1. NOTE and FILE the Los Angeles Organizing Committee for the Olympic and Paralympic Games 2028 (LA28) Impact and Sustainability Plan for the 2028 Olympic and Paralympic Games attached to the City Administrative Officer (CAO) report dated August 25, 2025, attached to the Council file. 2. REQUEST LA28 to make all procurement opportunities available on the Regional Alliance Marketplace for Procurement"
    },
    {
        "item_number": "11",
        "file_number": "25-0725",
        "title": "ARTS, PARKS, LIBRARIES, AND COMMUNITY ENRICHMENT and BUDGET AND FINANCE COMMITTEES\u2019 REPORT relative to a Work Plan for the Sunland Dog Park Project.",
        "description": "Recommendations for Council action, SUBJECT TO THE APPROVAL OF THE MAYOR: 1. AUTHORIZE the Department of Recreation and Parks (RAP) to submit a Work Plan as detailed in Attachment No. 1 to County of Los Angeles Regional Park and Open Space District"
    },
    {
        "item_number": "12",
        "file_number": "25-0689",
        "title": "HOUSING AND HOMELESSNESS and CIVIL RIGHTS, EQUITY, IMMIGRATION, AGING, AND DISABILITY COMMITTEES REPORT relative to the feasibility of the City establishing a Continuum of Care.",
        "description": "Recommendations for Council action, pursuant to Motion (Lee - Jurado): 1. INSTRUCT the Chief Legislative Analyst (CLA) to report to Council on the feasibility, potential benefits, and possible drawbacks of the City establishing its own Continuum of Care, independent of the County of Los Angeles (County). 2. INSTRUCT the Los Angeles Housing Department and the Community Investment for Families Department to report to Council on the structure of federal grants issued by the U.S. Department of Housing and Urban Development, and to assess how the City could remain competitive in securing funding under that structure if it were to operate its own Continuum of Care independent of the County. Fiscal Impact Statement: Neither the City Administrative Officer nor the CLA has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "13",
        "file_number": "17-1210",
        "title": "HOUSING AND HOMELESSNESS COMMITTEE REPORT relative to the reappointment of Cielo Castro to the Housing Authority of the City of Los Angeles Board of Commissioners (HACLA BOC).",
        "description": "Recommendation for Council action: RESOLVE that the Mayor\u2019s reappointment of Cielo Castro to the HACLA BOC for the term ending June 30, 2029, is APPROVED and CONFIRMED. Appointee currently resides in Council District 14. Appointee\u2019s current term expired on June 30, 2025. (Current Composition: M = 3; F = 3; Vacant = 1) Financial Disclosure Statement: Not applicable Community Impact Statement: None submitted"
    },
    {
        "item_number": "14",
        "file_number": "25-0862",
        "title": "HOUSING AND HOMELESSNESS COMMITTEE REPORT relative to extending Contract No. C-143351 with Coalition for Responsible Community Development for the Lincoln Theater emergency homeless housing site located at 2300 South Central Avenue.",
        "description": "Recommendation for Council action, pursuant to Motion (Price \u2013 Blumenfield): DIRECT and AUTHORIZE the City Clerk to extend the term of City Contract No. C-143351 with Coalition for Responsible Community Development for the purpose of defraying expenses associated with operating expenses related to the Lincoln Theater emergency homeless housing site located at 2300 South Central Avenue in Council District Nine to December 31, 2025. Fiscal Impact Statement: Neither the CAO nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "15",
        "file_number": "19-0126-S3",
        "title": "STATUTORY EXEMPTION and HOUSING AND HOMELESSNESS COMMITTEE REPORT relative to a lease extension and change in service provider for the A Bridge Home (ABH) site located at 3248",
        "description": ""
    },
    {
        "item_number": "16",
        "file_number": "25-0812",
        "title": "HOUSING AND HOMELESSNESS COMMITTEE REPORT relative to enhancements to the Systematic Code Enforcement Program (SCEP), Rent Escrow Account Program (REAP), and complaint-based inspection processes.",
        "description": "Recommendations for Council action: 1. INSTRUCT the General Manager, Los Angeles Housing Department (LAHD), or designee, to report to Council within 180 days on the following: a. The implementation progress for the recommended improvements for the SCEP and the REAP, including the distribution of enhanced educational materials, updated tenant rent escrow payment options, and revisions to the current Release of Escrow policy, procedures, and Rent Adjustment Commission (RAC) Regulations. b. Recommendations for the resolution of mold and lead- based paint conditions identified during inspections, including strengthening collaboration with the Los Angeles County Health Department. c. The SCEP cost recovery analysis, including REAP administrative fees and penalty assessments, to ensure that they reflect the program\u2019s operational costs. d. A list of problem properties within the REAP for prospective buyers to purchase from willing owners when feasible. e. Documenting the process for a tenant to petition for downward adjustments of rent. f. Resources required to prepare and provide inspection violation reports in a tenant's primary language, when known and available to the LAHD. g. Feasibility and resources needed to implement a temporary relocation or mitigation program when intrusive and extensive repairs are required. 2. INSTRUCT the LAHD to assist the RAC to amend the REAP Regulations to implement the enhanced procedures as outlined in the LAHD report dated July 23, 2025, attached to Council file No. 25-0812. 3. INSTRUCT the LAHD to amend Page No. 7, Section VI.3, entitled \u201cImproved Inspector Training \u2013 In Process,\u201d of the LAHD report dated July 23, 2025, attached to the Council file, to add language clarifying the LAHD\u2019s photography process. 4. AMEND Page No. 7, Section C.2, entitled \u201cNext Phase\u201d, of the LAHD report dated July 23, 2025, attached to the Council file, respectively, to read as follows (change in bold): Work with the RAC to revise REAP RAC Regulation 1200.00 to require allow that a final inspection, including inspection of all rental units, must be conducted prior to a property being released from REAP. 5. AMEND Page No. 4, Section I, entitled \u201cOutreach and Education for SCEP and REAP\u2019, of the LAHD report dated July 23, 2025, attached to the Council file, to add/create a \u201cNext Phase\u201d section, respectively, and add the following under the new section: a. Standardize the process whereby tenants are informed at the beginning of the process how to evaluate their new rent using the rent reduction calculator. b. Provide a public notification in a common area for tenants upon acceptance into the REAP. c. Provide tenant contact information to the outreach service provider upon placement into the REAP that stem from complaint-based inspections when contact information is available. 6. AMEND Page No. 6, Section IV, entitled \u201cStrengthen Resources for Problem Properties\u2019, of the LAHD report dated July 23, 2025, attached to the Council file, to add/create a \u201cNext Phase\u201d section, respectively, and add the following under the new section: a. As part of an improved case management process, ensure that new code violations discovered upon inspections that are not listed in the initial REAP complaint are cited and the REAP case is not closed until all violations are corrected. b. Establish a fast track process and prioritization for SCEP inspections of an entire building if one unit enters the REAP. c. Ensure that the REAP Unit formally communicates code violation complaints outside the scope of the REAP to all relevant LAHD sections and other agencies with enforcement authority. 7. AMEND Page No. 7, Section VI, entitled \u201cImproved Inspector Training \u2013 In Process,\u201d of the LAHD report dated July 23, 2025, attached to the Council file, to add/create a \u201cNext Phase\u201d section, respectively, and add the following under the new section: a. Provide training to Housing Inspectors on the importance of actively collaborating with outreach service providers and owners as an integral part of the REAP process. b. Provide training to Housing Inspectors to facilitate collection of tenant contact information for the purpose of sharing with outreach service providers. c. Provide training to Housing Inspectors to verify Tenant Protection postings at a property as required under the Los Angeles Municipal Code during inspections. 8. AMEND the language on Page No. 6, Section V.B.1, entitled \u201cIn Process\u201d, of the LAHD report dated July 23, 2025, attached to the Council file, respectively, to read as follows (change in bold): When a pattern of denied consent for inspection is observed, LAHD inspectors will inform tenants, outreach services providers, and landlords that the inspections are required by law, educate the tenants and landlords regarding the benefits of the inspection, as well as the limited allowable reasons for denying consent. This will also be incorporated in the \u201cLast Chance\u201d letter described below. 9. AMEND Page No. 7, Section V.C, entitled \u201cNext Phase\u201d, of the LAHD report dated July 23, 2025, attached to the Council file, respectively, to add the following: a. Immediately following the acceptance of a property into the REAP, generate an automated email notification to the appropriate Council Office. Fiscal Impact Statement: The LAHD reports that there is no impact to the General Fund. The SCEP and REAP program enhancements and future implementation recommendations are supported through the Systematic Code Enforcement Fee Fund No. 41M/43 and the Rent Stabilization Trust Fund No. 440/43. Community Impact Statement: None submitted"
    },
    {
        "item_number": "17",
        "file_number": "25-0928",
        "title": "PLANNING AND LAND USE MANAGEMENT COMMITTEE REPORT relative to establishing discussions regarding housing initiatives with the Los Angeles County Metropolitan Transit Authority (Metro), Los Angeles Unified School District (LAUSD), and the Los Angeles Community College District (LACCD).",
        "description": "Recommendations for Council action, pursuant to Motion (Padilla, Yaroslavsky - Raman): 1. INSTRUCT the Department of City Planning (DCP) to formally engage Metro, LAUSD, and LACCD for the purposes of establishing regularized, ongoing discussions regarding their respective housing initiatives, wherein the DCP can provide technical assistance, land use and zoning analyses, and updates on policy developments concerning land use and housing. 2. INSTRUCT the DCP to report to Council within 120 days on the following: a. Identifying limitations within existing City incentives for sites zoned for public facilities or owned by public agencies, and potential programmatic remedies. b. Furnishing recommendations to reduce any barriers for the timely approval and construction of dense, mixed-use multifamily developments and potential revenue generation opportunities at identified project sites and in the adjoining communities. 3. INSTRUCT the Chief Legislative Analyst (CLA), in consultation with the DCP, Department of Building and Safety, Los Angeles Housing Department, Los Angeles Fire Department, Department of Water and Power, Bureau of Sanitation, Department of Transportation, Department of Recreation and Parks, and Bureau of Street Services to report to Council within 120 days on recommendations to execute master development agreements and/or Memoranda of Understanding between the relevant departments and Metro, LAUSD, LACCD, and/or their development partners in order to reduce or streamline processes and timelines related to entitlements, inspections, permits, and approvals. The CLA shall review any agreements five years after execution, to assess for effectiveness, delivery of community-serving uses, and adherence to committed neighborhood engagement and accountability, and shall provide recommendations for potential modifications or repeal. Fiscal Impact Statement: Neither the City Administrative Officer nor the CLA has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "18",
        "file_number": "25-0758",
        "title": "PLANNING AND LAND USE MANAGEMENT COMMITTEE REPORT relative to creating a single, comprehensive review process for projects.",
        "description": "Recommendations for Council action, pursuant to Motion (Raman, Blumenfield \u2013 Yaroslavsky): 1. INSTRUCT the Department of Building and Safety (DBS) and Department of City Planning (DCP), with support from relevant departments as needed, to create a single, comprehensive review process for projects that includes the following: a. A summary of the most successful examples of coordinated input processes from other jurisdictions that can serve as models for Los Angeles. b. One coordinated plan check that incorporates all required department input. c. A clear and complete list of requirements provided at the outset. d. A process for collaboratively resolving conflicts arising from layered City requirements along with the applicant. e. Binding approvals and permit issuances valid for a reasonable timeframe, such that applicants are not subject to varying interpretations (i.e., \u201clate hits\u201d). 2. INSTRUCT the DBS and DCP to report to Council within 60 days with a framework for offering optional coordinated intake meetings, modeled on successful efforts in peer cities, that would allow applicants to meet with all relevant departments early in the process on a voluntary basis to receive consolidated requirements and determinations, and surface interdepartmental issues before plan submittal. 3. INSTRUCT the DBS to report to Council within 60 days on establishing a \u201csingle inspector\u201d model for projects, designating one lead inspector from pre-construction through final occupancy, to improve accountability and reduce contradictory directives. 4. INSTRUCT the DBS, with support from relevant departments as needed, to report to Council within 60 days on recommendations on how to significantly reduce and consolidate the number of separate plan check clearances and condition types, which exceed 175. 5. INSTRUCT the Bureau of Engineering and the DBS, in coordination with any other relevant departments, to report to Council within 60 days on the current and potential capabilities of BuildLA to facilitate simultaneous reviews, consolidate departmental input, resolve conflicts early, including feedback from system users, and to provide transparency on departmental timelines and any delays. Fiscal Impact Statement: Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: Yes For: Los Feliz Neighborhood Council Palms Neighborhood Council"
    },
    {
        "item_number": "19",
        "file_number": "25-0966",
        "title": "PLANNING AND LAND USE MANAGEMENT COMMITTEE REPORT relative to a pilot program for use of Artificial Intelligence (AI) tools for pre-screening of permit applications Recommendations for Council action, pursuant to Motion",
        "description": ""
    },
    {
        "item_number": "20",
        "file_number": "25-0810",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to the Narcotics Analysis Laboratory Trust Fund expenditure plan for Budget Fiscal Year (BFY) 2025-2026.",
        "description": "Recommendations for Council action, SUBJECT TO THE APPROVAL OF THE MAYOR: 1. AUTHORIZE the Controller to: a. Establish appropriation accounts within Fund No. 863/70 as follows: Account No. TBD, Casework Overtime; Amount: $10,000 Account No. TBD, Training, Travel, & Subscriptions; Amount: $70,000 Account No. TBD, Toxicology Analysis; Amount: $5,000 b. Increase appropriations as needed from Fund No. 863/70, account to be determined, to Fund No. 100/70, General Overtime Account No. 001090, by an amount not to exceed $10,000. 2. AUTHORIZE the Los Angeles Police Department to prepare the Controller\u2019s instructions for any technical adjustments, subject to the approval of the City Administrative Officer (CAO); and, AUTHORIZE and INSTRUCT the Controller to implement the instructions. 3. AUTHORIZE the Controller to re-appropriate funds from Fund No. 863/70, Account No. 70Y170, to Fund No. 100/70 (account to be determined), for BFY 2025-26 by an amount not to exceed $124,000. Fiscal Impact Statement: None submitted by the Board of Police Commissioners. Neither the CAO nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "21",
        "file_number": "25-0705",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to the request for payment of reward offer (DR No. 2212-09489) in a hit-and-run case.",
        "description": "Recommendations for Council action, SUBJECT TO THE APPROVAL OF THE MAYOR: 1. APPROVE the payment of $50,000 for information leading to the apprehension and conviction of the perpetrator in connection with a fatal hit-and-run case. (DR No. 2212-09489). 2. AUTHORIZE the Controller to transfer $50,000 from the Reserve Fund to the Unappropriated Balance, and appropriate therefrom to the Special Reward Trust Fund No. 436/14. 3. INSTRUCT the City Clerk to transfer $50,000 from the Special Reward Trust Fund No. 436/14, Account No. XXXXXX, to the Police Department Fund No. 100/70, Secret Service Account No. 004310. 4. INSTRUCT the Los Angeles Police Department to make the appropriate reward payment. Fiscal Impact Statement: None submitted by the Board of Police Commissioners. Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "22",
        "file_number": "25-0579",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to a non-monetary donation of Microsoft Co-Pilot licenses from the Los Angeles Police Foundation.",
        "description": "Recommendation for Council action: APPROVE the acceptance of a non-monetary donation of Microsoft Co-Pilot licenses, valued at $33,717.60, from the Los Angeles Police Foundation for the Los Angeles Police Department Information Technology Bureau; and, THANK the donor for this generous donation. Fiscal Impact Statement: None submitted by the Board of Police Commissioners. Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "23",
        "file_number": "25-0771",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to a non-monetary donation of Automated License Plate Recognition (ALPR) camera equipment from the Los Angeles Police Foundation.",
        "description": "Recommendation for Council action: APPROVE the acceptance of a non-monetary donation of APLR camera equipment, valued at $242,250, from the Los Angeles Police Foundation for the Los Angeles Police Department West Los Angeles Division; and, THANK the donor for this generous donation. Fiscal Impact Statement: None submitted by the Board of Police Commissioners. Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "24",
        "file_number": "25-0036",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to a non-monetary donation of Automated License Plate Recognition (ALPR) camera equipment from the Los Angeles Police Foundation.",
        "description": "Recommendation for Council action: APPROVE the acceptance of a non-monetary donation of APLR camera equipment, valued at $157,397.30, from the Los Angeles Police Foundation for the Los Angeles Police Department West Los Angeles Division; and, THANK the donor for this generous donation. Fiscal Impact Statement: None submitted by the Board of Police Commissioners. Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "25",
        "file_number": "25-0623",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to an in-kind donation of repair services from the Los Angeles Fire Department Foundation for fire stations and fire facilities.",
        "description": "Recommendation for Council action: APPROVE the acceptance of an in-kind donation of repair services, valued at approximately $9,000,000, from the Los Angeles Fire Department Foundation for fire stations and fire facilities; and, THANK the donor for this generous donation. Fiscal Impact Statement: None submitted by the Board of Fire Commissioners. Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "26",
        "file_number": "25-0839",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to the costs of responding to illegal fireworks over the July 4th weekend and the feasibility of a drone pilot program for illegal firework use.",
        "description": "Recommendations for Council action, pursuant to Motion (Lee \u2013 McOsker): 1. INSTRUCT the Los Angeles Fire Department to report to Council on the costs incurred by the City in responding to fires and other emergency calls caused by illegal fireworks over the most recent July 4th holiday weekend, including personnel, equipment, and property damage estimates. 2. INSTRUCT the Los Angeles Police Department, with the assistance of the City Attorney and any other relevant departments, to report to Council on the feasibility and cost of implementing a drone pilot program specifically during high- firework-use periods, such as the July 4th holiday, that would allow for real-time identification and administrative fines to be issued to homes and individuals responsible for the use of illegal fireworks. Fiscal Impact Statement: Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "27",
        "file_number": "23-0255-S1",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to improving 911 call response times for both emergency and non-emergency calls.",
        "description": "Recommendation for Council action, pursuant to Motion (Raman - Lee): INSTRUCT the Chief Legislative Analyst (CLA) and Los Angeles Police Department (LAPD), in consultation with the Mayor\u2019s Office of Community Safety, to report to Council within 30 days with recommendations to improve 911 call times for both emergency and non-emergency calls for service. This report should include, but not be limited to, the following: a. The staffing outlook for LAPD\u2019s Communications Division, including the projected impact of incoming Police Service Representatives (PSRs), as well as a detailed timeline and pipeline analysis of PSRs currently in training, and expected attrition rates for existing staff. b. An assessment of how the incoming PSRs are expected to impact emergency call response times and non- emergency hold times. c. An assessment of the impacts of integrating technological interventions for non-emergency call-taking successfully utilized in other jurisdictions. d. An evaluation of the feasibility of establishing dedicated non-emergency operators within the Communications Division to enhance service efficiency. e. An evaluation of the feasibility of creating a separate line tasked with dispatching unarmed crisis response teams, filing reports, and providing non-emergency assistance, including recommendations on where such a line could be housed, either within the City or externally. f. Recommendations for the kind of public education program required for effective rollout of any new efforts. Fiscal Impact Statement: Neither the City Administrative Officer nor the CLA has completed a financial analysis of this report. Community Impact Statement: Yes For: Westside Neighborhood Council"
    },
    {
        "item_number": "28",
        "file_number": "25-0378",
        "title": "PUBLIC WORKS COMMITTEE REPORT relative to the installation of the Venice Beach Ocean Front Walk Crash Ramps and Bollards Project.",
        "description": "Recommendations for Council action, pursuant to Motion (Park \u2013 Lee): 1. INSTRUCT the Bureau of Engineering to transfer the administration of Contract No. C-136817 to the Board of Public Works (BPW) upon completion of the installation phase of the Venice Beach Ocean Front Walk Crash Ramps and Bollards Project. 2. INSTRUCT the BPW to negotiate an amendment to said Contract to cover the more significant maintenance needs for the bollards, including but not limited to electrical faults, corrosion and other issues not covered under the maintenance aspects of the existing contract. 3. INSTRUCT the City Administrative Officer (CAO), with the assistance of the BPW, to identify a source of funds for the contract amendment as needed. 4. INSTRUCT the Los Angeles Police Department, Los Angeles Fire Department, and BPW to coordinate the dissemination of information on ingress and egress points to Ocean Front Walk to emergency personnel assigned to the area, in order to ensure that response times are not impacted by the bollards and crash ramps. Fiscal Impact Statement: Neither the CAO nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "29",
        "file_number": "25-0918",
        "title": "PUBLIC WORKS COMMITTEE REPORT relative to designating the intersection of Riverside Drive and Ponca Avenue as \u201cPhil Roman Square\".",
        "description": "Recommendations for Council action, pursuant to Motion (Nazarian \u2013 Padilla): 1. DESIGNATE the intersection of Riverside Drive and Ponca Avenue as \u201cPhil Roman Square\" to honor Phil Roman\u2019s extraordinary contributions to the animation industry, his enduring cultural legacy, and his deep connection to this neighborhood as the birthplace of Film Roman Studios. 2. DIRECT the Department of Transportation to erect permanent ceremonial signage at this location to reflect this dedication. Fiscal Impact Statement: Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "30",
        "file_number": "19-1200-S10",
        "title": "TRADE, TRAVEL AND TOURISM COMMITTEE REPORT relative to the reappointment of Nicholas Roxborough to the Board of Airport Commissioners for the term ending June 30, 2030.",
        "description": "Recommendation for Council action: RESOLVE that the Mayor\u2019s reappointment of Nicholas Roxborough to the Board of Airport Commissioners for the term ending June 30, 2030, is APPROVED and CONFIRMED. The appointee currently resides in Council District 4. (Current composition: M = 4; F = 3) Financial Disclosure Statement: Filed Community Impact Statement: None submitted TIME LIMIT FILE - SEPTEMBER 28, 2025"
    },
    {
        "item_number": "31",
        "file_number": "22-1200-S66",
        "title": "TRADE, TRAVEL AND TOURISM COMMITTEE REPORT relative to the reappointment of Matthew Johnson to the Board of Airport Commissioners for the term ending June 30, 2030.",
        "description": "Recommendation for Council action: RESOLVE that the Mayor\u2019s reappointment of Matthew Johnson to the Board of Airport Commissioners for the term ending June 30, 2030, is APPROVED and CONFIRMED. The appointee currently resides in Council District 5. (Current composition: M = 4; F = 3) Financial Disclosure Statement: Filed Community Impact Statement: None submitted TIME LIMIT FILE - SEPTEMBER 28, 2025"
    },
    {
        "item_number": "32",
        "file_number": "14-1064",
        "title": "CATEGORICAL EXEMPTION and TRADE, TRAVEL AND TOURISM COMMITTEE REPORT relative to the First Amendment to Airport Concessions Agreement No. LAA-9173 with Lenlyn Limited dba ICE Currency Services USA for currency exchange and business services concessions.",
        "description": "Recommendations for Council action: 1. CONCUR with the determination by the Board of Airport Commissioners (BOAC) that this action is categorically exempt from the California Environmental Quality Act (CEQA) pursuant to Article III, Class 1(18)(c) of the Los Angeles City CEQA Guidelines. 2. APPROVE the First Amendment to Concession Agreement No. LAA-9173 between the Los Angeles World Airports (LAWA) and Lenlyn Limited dba ICE Currency Services USA to extend the term through June 30, 2029, covering currency exchange and business services concessions at the Los Angeles International Airport (LAX). 3. CONCUR with the BOAC\u2019s action on June 5, 2025, by Resolution No. 28132, authorizing the Chief Executive Officer, LAWA, or designee, to execute said First Amendment to Concession Agreement No. LAA-9173 with Lenlyn Limited dba ICE Currency Services USA. Fiscal Impact Statement: The City Administrative Officer reports that approval of the proposed First Amendment to Concession Agreement No. LAA-9173 with Lenlyn Limited dba ICE Currency Services USA will have no impact on the General Fund. Revenue in the amount of at least $6 million is anticipated to be received during the extended two- year term and deposited under LAWA\u2019s Revenue Code 401070 \u2013 Foreign Exchange & Services. The recommendations in the report comply with the LAWA\u2019s adopted Financial Policies. Community Impact Statement: None submitted TIME LIMIT FILE - SEPTEMBER 12, 2025"
    },
    {
        "item_number": "33",
        "file_number": "15-0694",
        "title": "ADMINISTRATIVE EXEMPTION and TRADE, TRAVEL AND TOURISM COMMITTEE REPORT relative to the Sixth Amendment to Concession Agreement No. LAA-8862 with Boingo Wireless, Inc. covering wireless service at Los Angeles International Airport (LAX).",
        "description": "Recommendations for Council action: 1. CONCUR with the determination by the Board of Airport Commissioners (BOAC) that this action is administratively exempt from the California Environmental Quality Act (CEQA) pursuant to Article II, Section 2(f) of the Los Angeles City CEQA Guidelines. 2. APPROVE the Sixth Amendment to Concession Agreement No. LAA-8862 between Los Angeles World Airports (LAWA) and Boingo Wireless, Inc. to extend the term through June 30, 2026, covering wireless service at LAX. 3. CONCUR with the BOAC\u2019s action on June 5, 2025, by Resolution No. 28181, authorizing the Chief Executive Officer, LAWA, or designee, to execute said Sixth Amendment to Concession Agreement No. LAA-8862 with Boingo Wireless, Inc. Fiscal Impact Statement: The City Administrative Officer reports that approval of the proposed Sixth Amendment to Concession Agreement No. LAA-8862 with Boingo Wireless, Inc., for management and operation of the wireless network in all terminals at LAX will have no impact on the City\u2019s General Fund. Revenue in the amount of $1,400,000 is anticipated to be collected over the 12-month term includes a base annual fee ($583,000) and 50 percent of gross revenues of approximately $1,400,000 (anticipated to be $817,000). The base annual fee is subject to yearly rate escalations triggered by annual Consumer Price Index adjustments effective July 1st of each year. Revenues collected during the lease term will be allocated to the LAWA Revenue Fund. The recommendations in the report comply with the LAWA\u2019s adopted Financial Policies. Community Impact Statement: None submitted TIME LIMIT FILE - SEPTEMBER 12, 2025"
    },
    {
        "item_number": "34",
        "file_number": "25-0733",
        "title": "CDs 6, 11 TRADE, TRAVEL AND TOURISM COMMITTEE REPORT relative to protocols, policies, and procedures for requests by Immigration and Customs Enforcement (ICE) and other federal agents on City-owned airport property.",
        "description": "Recommendations for Council action, pursuant to Motion (Padilla \u2013 Park): 1. REQUEST the Los Angeles Word Airports (LAWA) to provide a verbal report to the full City Council, in closed session if necessary, within seven days, addressing the following: a. Alignment with City Attorney Guidance i. Procedures for areas not open to the general public"
    },
    {
        "item_number": "35",
        "file_number": "25-0811",
        "title": "CATEGORICAL EXEMPTION FROM THE CALIFORNIA ENVIRONMENTAL QUALITY ACT (CEQA) PURSUANT TO CEQA GUIDELINES, AND RELATED CEQA FINDINGS; COMMUNICATION FROM THE LOS ANGELES CITY PLANNING COMMISSION",
        "description": ""
    },
    {
        "item_number": "36",
        "file_number": "25-0781",
        "title": "CD 15 COMMUNICATION FROM THE PORT OF LOS ANGELES (POLA) and CONSIDERATION OF CALIFORNIA ENVIRONMENTAL QUALITY ACT (CEQA) SECTION 21151(C) APPEAL filed by UNITE HERE Local 11 of the action taken by the Board of Harbor Commissioners (BOHC) at its meeting held June 26, 2025, approving the Subsequent Environmental Impact Report (SEIR) for the West Harbor Modification project.",
        "description": ""
    },
    {
        "item_number": "37",
        "file_number": "25-0720",
        "title": "GOVERNMENT OPERATIONS and BUDGET AND FINANCE COMMITTEES\u2019 REPORT relative to the impacts of Cannabis taxation.",
        "description": "Recommendations for Council action, as initiated by Motion (Padilla \u2013 Yaroslavsky): 1. INSTRUCT the City Administrative Officer (CAO) to report to Council with an analysis relative to the revenue impacts of the 19 percent California cannabis excise tax that will come to effect on July 1, 2025. 2. INSTRUCT the CAO to identify funds and issue a solicitation seeking an outside economic analysis of the potential economic impacts of lowering the City's cannabis tax rate to 1.5 percent, 3 percent, 5 percent, and 8 percent. 3. INSTRUCT the CAO and REQUEST the City Attorney to report to Council on the feasibility of instituting a cannabis tax policy that is structured like that of the City of Oakland. 4. DIRECT that the Cannabis Regulation Commission report dated July 18, 2025, attached to Council file No. 25-0720, be transferred to a new Council file. Fiscal Impact Statement: None submitted by the Cannabis Regulation Commission. Neither the CAO nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted."
    },
    {
        "item_number": "38",
        "file_number": "25-0753",
        "title": "PLANNING AND LAND USE MANAGEMENT COMMITTEE REPORT relative to a requested ordinance to implement Assembly Bill (AB) 1033 (Ting, Chapter 752, Statutes of 2023).",
        "description": "Recommendation for Council action, pursuant to Motion (Raman - Blumenfield): INSTRUCT the Department of City Planning, with the assistance of the City Attorney, to prepare and present an ordinance to implement AB 1033 (Ting, Chapter 752, Statutes of 2023), which authorizes local agencies to adopt a local ordinance to allow accessory dwelling units (ADUs) to be sold separately or conveyed from the primary residence as condominiums. Fiscal Impact Statement: Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: Yes For: Los Feliz Neighborhood Council Palms Neighborhood Council Against: Sunland-Tujunga Neighborhood Council Items for which Public Hearings Have Not Been Held - (10 Votes Required for Consideration)"
    },
    {
        "item_number": "39",
        "file_number": "25-1031",
        "title": "MOTION (LEE - HUTT) relative to funding for the installation of signage in Council District 12.",
        "description": "Recommendations for Council action, SUBJECT TO THE APPROVAL OF THE MAYOR: 1. TRANSFER AND APPROPRIATE $7,536.09 from the AB1290 Fund No. 53P, Account No. 281212 (CD 12 Redevelopment Projects - Services) to the Department of Transportation Fund No.100/94, Account No. 003040 (Contractual Services), for installation of signage. 2. AUTHORIZE the City Clerk and/or the Department of Transportation to make any corrections, clarifications, or revisions to the above fund transfer instructions, including any new instructions, in order to effectuate the intent of this Motion, and including any corrections and changes to fund or account numbers; said corrections/clarifications/changes may be made orally, electronically, or by any other means."
    },
    {
        "item_number": "40",
        "file_number": "25-0030",
        "title": "RESOLUTION (HARRIS-DAWSON - BLUMENFIELD) relative to the Declaration of Local Emergency by the Mayor dated January 7, 2025, and Updated Declaration of Local Emergency by the Mayor dated January 13, 2025, due to the windstorm and extreme fire weather system and devastating wildfires in the City of Los Angeles (City), pursuant to Los Angeles Administrative Code (LAAC) Section 8.27.",
        "description": "Recommendation for Council action: ADOPT the accompanying RESOLUTION, dated January 14, 2025, to: 1. Resolve that a local emergency exists resulting from ongoing windstorm and extreme fire weather system and the devastating wildfires in the City within the meaning of LAAC Section 8.21, et seq., as set forth in the Mayor\u2019s January 13, 2025 Updated Declaration of Local Emergency, which incorporated the declaration of emergency dated January 7, 2025, which the City Council hereby ratifies. 2. Resolve that because the local emergency, which began on January 7, 2025, continues to exist, there is a need to continue the state of local emergency, which the City Council hereby ratifies. 3. Instruct and request all appropriate City departments (including proprietary departments), agencies, and personnel, in accordance with LAAC Code Section 8.21 et seq., to continue to perform all duties and responsibilities to represent the City in this matter to respond to and abate the emergency and prevent further harm to the life, health, property, and safety, and receive, process; and, coordinate all inquiries and requirements necessary to obtain whatever State and Federal assistance that may become available to the City and/or to the citizens of the City who may be affected by the emergency. 4. Instruct the General Manager, Emergency Management Department, to advise the Mayor and City Council on the need to extend the state of local emergency, as appropriate. 5. Resolve that, to the extent the public interest and necessity demand the immediate expenditure of public funds to safeguard life, health, or property in response to the local emergency and to support the emergency operations of the City and its departments (including its proprietary departments), agencies, and personnel (including mutual aid resources) in responding to the declared local emergency, the competitive bidding requirements enumerated in City Charter Section 371, and further codified in the LAAC, including LAAC Section 10.15 be suspended until termination of the state of emergency and solely with respect to purchases and contracts needed to respond to the declared state of emergency. 6. Direct and request City departments and agencies making purchases pursuant to the authority granted in paragraph five"
    }
] $$::jsonb
  ) AS j
)
INSERT INTO public."AgendaItems"
  ("MeetingID","Title","Description","ItemNumber","OrderNumber","FileNumber")
SELECT
  (SELECT mid FROM m),
  s.title,
  s.description,
  s.item_number,
  s.item_number,   
  s.file_number
FROM src s;

-- Insert agenda items for Sep 10, 2025
WITH m AS (
  SELECT "MeetingID" AS mid FROM public."Meetings" WHERE "Date" = '2025-09-10'
),
src AS (
  SELECT
    (j->>'item_number')::int            AS item_number,
    j->>'file_number'                   AS file_number,
    j->>'title'                         AS title,
    COALESCE(j->>'description','')      AS description
  FROM jsonb_array_elements(
    $$ [
    {
        "item_number": "1",
        "file_number": "25-0160-S70",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 1717 West 6th Street.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 1717 West 6th Street. (Lien: $2,624.54)"
    },
    {
        "item_number": "2",
        "file_number": "14-0160-S418",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 1546 West 7th Street.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 1546 West 7th Street. (Lien: $1,483.26)"
    },
    {
        "item_number": "3",
        "file_number": "25-0160-S69",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 5534 North Cantaloupe Avenue.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 5534 North Cantaloupe Avenue. (Lien: $1,276.56)"
    },
    {
        "item_number": "4",
        "file_number": "25-0160-S83",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 6803 North Aldea Avenue.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 6803 North Aldea Avenue. (Lien: $2,644.84)"
    },
    {
        "item_number": "5",
        "file_number": "25-0160-S103",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 7708 North Beck Avenue.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 7708 North Beck Avenue. (Lien: $1,276.56)"
    },
    {
        "item_number": "6",
        "file_number": "14-0160-S447",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 11366 North Oro Vista Avenue.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 11366 North Oro Vista Avenue. (Lien: $2,604.55)"
    },
    {
        "item_number": "7",
        "file_number": "16-0160-S284",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 1541 West Florence Avenue.",
        "description": "Recommendation for Council action: PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 1541 West Florence Avenue. (Lien: $4,547.58)"
    },
    {
        "item_number": "8",
        "file_number": "25-0160-S72",
        "title": "CONTINUED CONSIDERATION OF HEARING PROTEST, APPEALS OR OBJECTIONS to the Department of Building and Safety report and confirmation of lien for nuisance abatement costs and/or non- compliance of code violations/Annual Inspection costs for the property located at 572 East M Street.",
        "description": "Recommendation for Council action: HEAR PROTEST, APPEALS OR OBJECTIONS relative to a proposed lien for nuisance abatement costs and/or non-compliance of code violations/Annual Inspection costs, pursuant to the Los Angeles Municipal Code and/or Los Angeles Administrative Code, and CONFIRM said lien for the property located at 572 East M Street."
    },
    {
        "item_number": "9",
        "file_number": "15-0989-S44",
        "title": "AD HOC COMMITTEE ON THE 2028 OLYMPICS AND PARALYMPIC GAMES REPORT relative to the Second Amendment to the Venue Plan for the 2028 Olympic and Paralympic Games.",
        "description": "Recommendations for Council action: 1. APPROVE the Second Amendment to the Venue Plan for the 2028 Olympic and Paralympic Games, in accordance with Section 6.6 of the Games Agreement, to authorize the relocation of the Aquatics Diving sports discipline from a venue in the City of Los Angeles to a venue in the City of Pasadena, California, contingent upon completion of a signed definitive agreement between the Los Angeles Organizing Committee for the Olympic and Paralympic Games 2028 (LA28) and the Department of Recreation and Parks (RAP) regarding the licensing and right to access the John C. Argue Swim Stadium at Exposition Park and a commitment by LA 28 to undertake efforts to bring it to national and international competition standards in order to create a lasting community benefit. 2. INSTRUCT the RAP, and REQUEST LA28, to report to Council on the definitive agreement regarding the licensing and right to access the John C. Argue Swim Stadium at Exposition Park and the commitment by LA28 to undertake efforts to bring it to national and international competition standards in order to create a lasting community benefit. Fiscal Impact Statement: The Chief Legislative Analyst and City Administrative Officer report that there is no fiscal impact resulting from the recommendations in the report. Community Impact Statement: None Submitted"
    },
    {
        "item_number": "10",
        "file_number": "15-0989-S51",
        "title": "AD HOC COMMITTEE ON THE 2028 OLYMPICS AND PARALYMPIC GAMES REPORT relative to the LA28 Impact and Sustainability Plan for the 2028 Olympic and Paralympic Games.",
        "description": "Recommendations for Council action: 1. NOTE and FILE the Los Angeles Organizing Committee for the Olympic and Paralympic Games 2028 (LA28) Impact and Sustainability Plan for the 2028 Olympic and Paralympic Games attached to the City Administrative Officer (CAO) report dated August 25, 2025, attached to the Council file. 2. REQUEST LA28 to make all procurement opportunities available on the Regional Alliance Marketplace for Procurement"
    },
    {
        "item_number": "11",
        "file_number": "25-0725",
        "title": "ARTS, PARKS, LIBRARIES, AND COMMUNITY ENRICHMENT and BUDGET AND FINANCE COMMITTEES\u2019 REPORT relative to a Work Plan for the Sunland Dog Park Project.",
        "description": "Recommendations for Council action, SUBJECT TO THE APPROVAL OF THE MAYOR: 1. AUTHORIZE the Department of Recreation and Parks (RAP) to submit a Work Plan as detailed in Attachment No. 1 to County of Los Angeles Regional Park and Open Space District"
    },
    {
        "item_number": "12",
        "file_number": "25-0689",
        "title": "HOUSING AND HOMELESSNESS and CIVIL RIGHTS, EQUITY, IMMIGRATION, AGING, AND DISABILITY COMMITTEES REPORT relative to the feasibility of the City establishing a Continuum of Care.",
        "description": "Recommendations for Council action, pursuant to Motion (Lee - Jurado): 1. INSTRUCT the Chief Legislative Analyst (CLA) to report to Council on the feasibility, potential benefits, and possible drawbacks of the City establishing its own Continuum of Care, independent of the County of Los Angeles (County). 2. INSTRUCT the Los Angeles Housing Department and the Community Investment for Families Department to report to Council on the structure of federal grants issued by the U.S. Department of Housing and Urban Development, and to assess how the City could remain competitive in securing funding under that structure if it were to operate its own Continuum of Care independent of the County. Fiscal Impact Statement: Neither the City Administrative Officer nor the CLA has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "13",
        "file_number": "17-1210",
        "title": "HOUSING AND HOMELESSNESS COMMITTEE REPORT relative to the reappointment of Cielo Castro to the Housing Authority of the City of Los Angeles Board of Commissioners (HACLA BOC).",
        "description": "Recommendation for Council action: RESOLVE that the Mayor\u2019s reappointment of Cielo Castro to the HACLA BOC for the term ending June 30, 2029, is APPROVED and CONFIRMED. Appointee currently resides in Council District 14. Appointee\u2019s current term expired on June 30, 2025. (Current Composition: M = 3; F = 3; Vacant = 1) Financial Disclosure Statement: Not applicable Community Impact Statement: None submitted"
    },
    {
        "item_number": "14",
        "file_number": "25-0862",
        "title": "HOUSING AND HOMELESSNESS COMMITTEE REPORT relative to extending Contract No. C-143351 with Coalition for Responsible Community Development for the Lincoln Theater emergency homeless housing site located at 2300 South Central Avenue.",
        "description": "Recommendation for Council action, pursuant to Motion (Price \u2013 Blumenfield): DIRECT and AUTHORIZE the City Clerk to extend the term of City Contract No. C-143351 with Coalition for Responsible Community Development for the purpose of defraying expenses associated with operating expenses related to the Lincoln Theater emergency homeless housing site located at 2300 South Central Avenue in Council District Nine to December 31, 2025. Fiscal Impact Statement: Neither the CAO nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "15",
        "file_number": "19-0126-S3",
        "title": "STATUTORY EXEMPTION and HOUSING AND HOMELESSNESS COMMITTEE REPORT relative to a lease extension and change in service provider for the A Bridge Home (ABH) site located at 3248",
        "description": ""
    },
    {
        "item_number": "16",
        "file_number": "25-0812",
        "title": "HOUSING AND HOMELESSNESS COMMITTEE REPORT relative to enhancements to the Systematic Code Enforcement Program (SCEP), Rent Escrow Account Program (REAP), and complaint-based inspection processes.",
        "description": "Recommendations for Council action: 1. INSTRUCT the General Manager, Los Angeles Housing Department (LAHD), or designee, to report to Council within 180 days on the following: a. The implementation progress for the recommended improvements for the SCEP and the REAP, including the distribution of enhanced educational materials, updated tenant rent escrow payment options, and revisions to the current Release of Escrow policy, procedures, and Rent Adjustment Commission (RAC) Regulations. b. Recommendations for the resolution of mold and lead- based paint conditions identified during inspections, including strengthening collaboration with the Los Angeles County Health Department. c. The SCEP cost recovery analysis, including REAP administrative fees and penalty assessments, to ensure that they reflect the program\u2019s operational costs. d. A list of problem properties within the REAP for prospective buyers to purchase from willing owners when feasible. e. Documenting the process for a tenant to petition for downward adjustments of rent. f. Resources required to prepare and provide inspection violation reports in a tenant's primary language, when known and available to the LAHD. g. Feasibility and resources needed to implement a temporary relocation or mitigation program when intrusive and extensive repairs are required. 2. INSTRUCT the LAHD to assist the RAC to amend the REAP Regulations to implement the enhanced procedures as outlined in the LAHD report dated July 23, 2025, attached to Council file No. 25-0812. 3. INSTRUCT the LAHD to amend Page No. 7, Section VI.3, entitled \u201cImproved Inspector Training \u2013 In Process,\u201d of the LAHD report dated July 23, 2025, attached to the Council file, to add language clarifying the LAHD\u2019s photography process. 4. AMEND Page No. 7, Section C.2, entitled \u201cNext Phase\u201d, of the LAHD report dated July 23, 2025, attached to the Council file, respectively, to read as follows (change in bold): Work with the RAC to revise REAP RAC Regulation 1200.00 to require allow that a final inspection, including inspection of all rental units, must be conducted prior to a property being released from REAP. 5. AMEND Page No. 4, Section I, entitled \u201cOutreach and Education for SCEP and REAP\u2019, of the LAHD report dated July 23, 2025, attached to the Council file, to add/create a \u201cNext Phase\u201d section, respectively, and add the following under the new section: a. Standardize the process whereby tenants are informed at the beginning of the process how to evaluate their new rent using the rent reduction calculator. b. Provide a public notification in a common area for tenants upon acceptance into the REAP. c. Provide tenant contact information to the outreach service provider upon placement into the REAP that stem from complaint-based inspections when contact information is available. 6. AMEND Page No. 6, Section IV, entitled \u201cStrengthen Resources for Problem Properties\u2019, of the LAHD report dated July 23, 2025, attached to the Council file, to add/create a \u201cNext Phase\u201d section, respectively, and add the following under the new section: a. As part of an improved case management process, ensure that new code violations discovered upon inspections that are not listed in the initial REAP complaint are cited and the REAP case is not closed until all violations are corrected. b. Establish a fast track process and prioritization for SCEP inspections of an entire building if one unit enters the REAP. c. Ensure that the REAP Unit formally communicates code violation complaints outside the scope of the REAP to all relevant LAHD sections and other agencies with enforcement authority. 7. AMEND Page No. 7, Section VI, entitled \u201cImproved Inspector Training \u2013 In Process,\u201d of the LAHD report dated July 23, 2025, attached to the Council file, to add/create a \u201cNext Phase\u201d section, respectively, and add the following under the new section: a. Provide training to Housing Inspectors on the importance of actively collaborating with outreach service providers and owners as an integral part of the REAP process. b. Provide training to Housing Inspectors to facilitate collection of tenant contact information for the purpose of sharing with outreach service providers. c. Provide training to Housing Inspectors to verify Tenant Protection postings at a property as required under the Los Angeles Municipal Code during inspections. 8. AMEND the language on Page No. 6, Section V.B.1, entitled \u201cIn Process\u201d, of the LAHD report dated July 23, 2025, attached to the Council file, respectively, to read as follows (change in bold): When a pattern of denied consent for inspection is observed, LAHD inspectors will inform tenants, outreach services providers, and landlords that the inspections are required by law, educate the tenants and landlords regarding the benefits of the inspection, as well as the limited allowable reasons for denying consent. This will also be incorporated in the \u201cLast Chance\u201d letter described below. 9. AMEND Page No. 7, Section V.C, entitled \u201cNext Phase\u201d, of the LAHD report dated July 23, 2025, attached to the Council file, respectively, to add the following: a. Immediately following the acceptance of a property into the REAP, generate an automated email notification to the appropriate Council Office. Fiscal Impact Statement: The LAHD reports that there is no impact to the General Fund. The SCEP and REAP program enhancements and future implementation recommendations are supported through the Systematic Code Enforcement Fee Fund No. 41M/43 and the Rent Stabilization Trust Fund No. 440/43. Community Impact Statement: None submitted"
    },
    {
        "item_number": "17",
        "file_number": "25-0928",
        "title": "PLANNING AND LAND USE MANAGEMENT COMMITTEE REPORT relative to establishing discussions regarding housing initiatives with the Los Angeles County Metropolitan Transit Authority (Metro), Los Angeles Unified School District (LAUSD), and the Los Angeles Community College District (LACCD).",
        "description": "Recommendations for Council action, pursuant to Motion (Padilla, Yaroslavsky - Raman): 1. INSTRUCT the Department of City Planning (DCP) to formally engage Metro, LAUSD, and LACCD for the purposes of establishing regularized, ongoing discussions regarding their respective housing initiatives, wherein the DCP can provide technical assistance, land use and zoning analyses, and updates on policy developments concerning land use and housing. 2. INSTRUCT the DCP to report to Council within 120 days on the following: a. Identifying limitations within existing City incentives for sites zoned for public facilities or owned by public agencies, and potential programmatic remedies. b. Furnishing recommendations to reduce any barriers for the timely approval and construction of dense, mixed-use multifamily developments and potential revenue generation opportunities at identified project sites and in the adjoining communities. 3. INSTRUCT the Chief Legislative Analyst (CLA), in consultation with the DCP, Department of Building and Safety, Los Angeles Housing Department, Los Angeles Fire Department, Department of Water and Power, Bureau of Sanitation, Department of Transportation, Department of Recreation and Parks, and Bureau of Street Services to report to Council within 120 days on recommendations to execute master development agreements and/or Memoranda of Understanding between the relevant departments and Metro, LAUSD, LACCD, and/or their development partners in order to reduce or streamline processes and timelines related to entitlements, inspections, permits, and approvals. The CLA shall review any agreements five years after execution, to assess for effectiveness, delivery of community-serving uses, and adherence to committed neighborhood engagement and accountability, and shall provide recommendations for potential modifications or repeal. Fiscal Impact Statement: Neither the City Administrative Officer nor the CLA has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "18",
        "file_number": "25-0758",
        "title": "PLANNING AND LAND USE MANAGEMENT COMMITTEE REPORT relative to creating a single, comprehensive review process for projects.",
        "description": "Recommendations for Council action, pursuant to Motion (Raman, Blumenfield \u2013 Yaroslavsky): 1. INSTRUCT the Department of Building and Safety (DBS) and Department of City Planning (DCP), with support from relevant departments as needed, to create a single, comprehensive review process for projects that includes the following: a. A summary of the most successful examples of coordinated input processes from other jurisdictions that can serve as models for Los Angeles. b. One coordinated plan check that incorporates all required department input. c. A clear and complete list of requirements provided at the outset. d. A process for collaboratively resolving conflicts arising from layered City requirements along with the applicant. e. Binding approvals and permit issuances valid for a reasonable timeframe, such that applicants are not subject to varying interpretations (i.e., \u201clate hits\u201d). 2. INSTRUCT the DBS and DCP to report to Council within 60 days with a framework for offering optional coordinated intake meetings, modeled on successful efforts in peer cities, that would allow applicants to meet with all relevant departments early in the process on a voluntary basis to receive consolidated requirements and determinations, and surface interdepartmental issues before plan submittal. 3. INSTRUCT the DBS to report to Council within 60 days on establishing a \u201csingle inspector\u201d model for projects, designating one lead inspector from pre-construction through final occupancy, to improve accountability and reduce contradictory directives. 4. INSTRUCT the DBS, with support from relevant departments as needed, to report to Council within 60 days on recommendations on how to significantly reduce and consolidate the number of separate plan check clearances and condition types, which exceed 175. 5. INSTRUCT the Bureau of Engineering and the DBS, in coordination with any other relevant departments, to report to Council within 60 days on the current and potential capabilities of BuildLA to facilitate simultaneous reviews, consolidate departmental input, resolve conflicts early, including feedback from system users, and to provide transparency on departmental timelines and any delays. Fiscal Impact Statement: Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: Yes For: Los Feliz Neighborhood Council Palms Neighborhood Council"
    },
    {
        "item_number": "19",
        "file_number": "25-0966",
        "title": "PLANNING AND LAND USE MANAGEMENT COMMITTEE REPORT relative to a pilot program for use of Artificial Intelligence (AI) tools for pre-screening of permit applications Recommendations for Council action, pursuant to Motion",
        "description": ""
    },
    {
        "item_number": "20",
        "file_number": "25-0810",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to the Narcotics Analysis Laboratory Trust Fund expenditure plan for Budget Fiscal Year (BFY) 2025-2026.",
        "description": "Recommendations for Council action, SUBJECT TO THE APPROVAL OF THE MAYOR: 1. AUTHORIZE the Controller to: a. Establish appropriation accounts within Fund No. 863/70 as follows: Account No. TBD, Casework Overtime; Amount: $10,000 Account No. TBD, Training, Travel, & Subscriptions; Amount: $70,000 Account No. TBD, Toxicology Analysis; Amount: $5,000 b. Increase appropriations as needed from Fund No. 863/70, account to be determined, to Fund No. 100/70, General Overtime Account No. 001090, by an amount not to exceed $10,000. 2. AUTHORIZE the Los Angeles Police Department to prepare the Controller\u2019s instructions for any technical adjustments, subject to the approval of the City Administrative Officer (CAO); and, AUTHORIZE and INSTRUCT the Controller to implement the instructions. 3. AUTHORIZE the Controller to re-appropriate funds from Fund No. 863/70, Account No. 70Y170, to Fund No. 100/70 (account to be determined), for BFY 2025-26 by an amount not to exceed $124,000. Fiscal Impact Statement: None submitted by the Board of Police Commissioners. Neither the CAO nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "21",
        "file_number": "25-0705",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to the request for payment of reward offer (DR No. 2212-09489) in a hit-and-run case.",
        "description": "Recommendations for Council action, SUBJECT TO THE APPROVAL OF THE MAYOR: 1. APPROVE the payment of $50,000 for information leading to the apprehension and conviction of the perpetrator in connection with a fatal hit-and-run case. (DR No. 2212-09489). 2. AUTHORIZE the Controller to transfer $50,000 from the Reserve Fund to the Unappropriated Balance, and appropriate therefrom to the Special Reward Trust Fund No. 436/14. 3. INSTRUCT the City Clerk to transfer $50,000 from the Special Reward Trust Fund No. 436/14, Account No. XXXXXX, to the Police Department Fund No. 100/70, Secret Service Account No. 004310. 4. INSTRUCT the Los Angeles Police Department to make the appropriate reward payment. Fiscal Impact Statement: None submitted by the Board of Police Commissioners. Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "22",
        "file_number": "25-0579",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to a non-monetary donation of Microsoft Co-Pilot licenses from the Los Angeles Police Foundation.",
        "description": "Recommendation for Council action: APPROVE the acceptance of a non-monetary donation of Microsoft Co-Pilot licenses, valued at $33,717.60, from the Los Angeles Police Foundation for the Los Angeles Police Department Information Technology Bureau; and, THANK the donor for this generous donation. Fiscal Impact Statement: None submitted by the Board of Police Commissioners. Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "23",
        "file_number": "25-0771",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to a non-monetary donation of Automated License Plate Recognition (ALPR) camera equipment from the Los Angeles Police Foundation.",
        "description": "Recommendation for Council action: APPROVE the acceptance of a non-monetary donation of APLR camera equipment, valued at $242,250, from the Los Angeles Police Foundation for the Los Angeles Police Department West Los Angeles Division; and, THANK the donor for this generous donation. Fiscal Impact Statement: None submitted by the Board of Police Commissioners. Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "24",
        "file_number": "25-0036",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to a non-monetary donation of Automated License Plate Recognition (ALPR) camera equipment from the Los Angeles Police Foundation.",
        "description": "Recommendation for Council action: APPROVE the acceptance of a non-monetary donation of APLR camera equipment, valued at $157,397.30, from the Los Angeles Police Foundation for the Los Angeles Police Department West Los Angeles Division; and, THANK the donor for this generous donation. Fiscal Impact Statement: None submitted by the Board of Police Commissioners. Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "25",
        "file_number": "25-0623",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to an in-kind donation of repair services from the Los Angeles Fire Department Foundation for fire stations and fire facilities.",
        "description": "Recommendation for Council action: APPROVE the acceptance of an in-kind donation of repair services, valued at approximately $9,000,000, from the Los Angeles Fire Department Foundation for fire stations and fire facilities; and, THANK the donor for this generous donation. Fiscal Impact Statement: None submitted by the Board of Fire Commissioners. Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "26",
        "file_number": "25-0839",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to the costs of responding to illegal fireworks over the July 4th weekend and the feasibility of a drone pilot program for illegal firework use.",
        "description": "Recommendations for Council action, pursuant to Motion (Lee \u2013 McOsker): 1. INSTRUCT the Los Angeles Fire Department to report to Council on the costs incurred by the City in responding to fires and other emergency calls caused by illegal fireworks over the most recent July 4th holiday weekend, including personnel, equipment, and property damage estimates. 2. INSTRUCT the Los Angeles Police Department, with the assistance of the City Attorney and any other relevant departments, to report to Council on the feasibility and cost of implementing a drone pilot program specifically during high- firework-use periods, such as the July 4th holiday, that would allow for real-time identification and administrative fines to be issued to homes and individuals responsible for the use of illegal fireworks. Fiscal Impact Statement: Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "27",
        "file_number": "23-0255-S1",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to improving 911 call response times for both emergency and non-emergency calls.",
        "description": "Recommendation for Council action, pursuant to Motion (Raman - Lee): INSTRUCT the Chief Legislative Analyst (CLA) and Los Angeles Police Department (LAPD), in consultation with the Mayor\u2019s Office of Community Safety, to report to Council within 30 days with recommendations to improve 911 call times for both emergency and non-emergency calls for service. This report should include, but not be limited to, the following: a. The staffing outlook for LAPD\u2019s Communications Division, including the projected impact of incoming Police Service Representatives (PSRs), as well as a detailed timeline and pipeline analysis of PSRs currently in training, and expected attrition rates for existing staff. b. An assessment of how the incoming PSRs are expected to impact emergency call response times and non- emergency hold times. c. An assessment of the impacts of integrating technological interventions for non-emergency call-taking successfully utilized in other jurisdictions. d. An evaluation of the feasibility of establishing dedicated non-emergency operators within the Communications Division to enhance service efficiency. e. An evaluation of the feasibility of creating a separate line tasked with dispatching unarmed crisis response teams, filing reports, and providing non-emergency assistance, including recommendations on where such a line could be housed, either within the City or externally. f. Recommendations for the kind of public education program required for effective rollout of any new efforts. Fiscal Impact Statement: Neither the City Administrative Officer nor the CLA has completed a financial analysis of this report. Community Impact Statement: Yes For: Westside Neighborhood Council"
    },
    {
        "item_number": "28",
        "file_number": "25-0378",
        "title": "PUBLIC WORKS COMMITTEE REPORT relative to the installation of the Venice Beach Ocean Front Walk Crash Ramps and Bollards Project.",
        "description": "Recommendations for Council action, pursuant to Motion (Park \u2013 Lee): 1. INSTRUCT the Bureau of Engineering to transfer the administration of Contract No. C-136817 to the Board of Public Works (BPW) upon completion of the installation phase of the Venice Beach Ocean Front Walk Crash Ramps and Bollards Project. 2. INSTRUCT the BPW to negotiate an amendment to said Contract to cover the more significant maintenance needs for the bollards, including but not limited to electrical faults, corrosion and other issues not covered under the maintenance aspects of the existing contract. 3. INSTRUCT the City Administrative Officer (CAO), with the assistance of the BPW, to identify a source of funds for the contract amendment as needed. 4. INSTRUCT the Los Angeles Police Department, Los Angeles Fire Department, and BPW to coordinate the dissemination of information on ingress and egress points to Ocean Front Walk to emergency personnel assigned to the area, in order to ensure that response times are not impacted by the bollards and crash ramps. Fiscal Impact Statement: Neither the CAO nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "29",
        "file_number": "25-0918",
        "title": "PUBLIC WORKS COMMITTEE REPORT relative to designating the intersection of Riverside Drive and Ponca Avenue as \u201cPhil Roman Square\".",
        "description": "Recommendations for Council action, pursuant to Motion (Nazarian \u2013 Padilla): 1. DESIGNATE the intersection of Riverside Drive and Ponca Avenue as \u201cPhil Roman Square\" to honor Phil Roman\u2019s extraordinary contributions to the animation industry, his enduring cultural legacy, and his deep connection to this neighborhood as the birthplace of Film Roman Studios. 2. DIRECT the Department of Transportation to erect permanent ceremonial signage at this location to reflect this dedication. Fiscal Impact Statement: Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "30",
        "file_number": "19-1200-S10",
        "title": "TRADE, TRAVEL AND TOURISM COMMITTEE REPORT relative to the reappointment of Nicholas Roxborough to the Board of Airport Commissioners for the term ending June 30, 2030.",
        "description": "Recommendation for Council action: RESOLVE that the Mayor\u2019s reappointment of Nicholas Roxborough to the Board of Airport Commissioners for the term ending June 30, 2030, is APPROVED and CONFIRMED. The appointee currently resides in Council District 4. (Current composition: M = 4; F = 3) Financial Disclosure Statement: Filed Community Impact Statement: None submitted TIME LIMIT FILE - SEPTEMBER 28, 2025"
    },
    {
        "item_number": "31",
        "file_number": "22-1200-S66",
        "title": "TRADE, TRAVEL AND TOURISM COMMITTEE REPORT relative to the reappointment of Matthew Johnson to the Board of Airport Commissioners for the term ending June 30, 2030.",
        "description": "Recommendation for Council action: RESOLVE that the Mayor\u2019s reappointment of Matthew Johnson to the Board of Airport Commissioners for the term ending June 30, 2030, is APPROVED and CONFIRMED. The appointee currently resides in Council District 5. (Current composition: M = 4; F = 3) Financial Disclosure Statement: Filed Community Impact Statement: None submitted TIME LIMIT FILE - SEPTEMBER 28, 2025"
    },
    {
        "item_number": "32",
        "file_number": "14-1064",
        "title": "CATEGORICAL EXEMPTION and TRADE, TRAVEL AND TOURISM COMMITTEE REPORT relative to the First Amendment to Airport Concessions Agreement No. LAA-9173 with Lenlyn Limited dba ICE Currency Services USA for currency exchange and business services concessions.",
        "description": "Recommendations for Council action: 1. CONCUR with the determination by the Board of Airport Commissioners (BOAC) that this action is categorically exempt from the California Environmental Quality Act (CEQA) pursuant to Article III, Class 1(18)(c) of the Los Angeles City CEQA Guidelines. 2. APPROVE the First Amendment to Concession Agreement No. LAA-9173 between the Los Angeles World Airports (LAWA) and Lenlyn Limited dba ICE Currency Services USA to extend the term through June 30, 2029, covering currency exchange and business services concessions at the Los Angeles International Airport (LAX). 3. CONCUR with the BOAC\u2019s action on June 5, 2025, by Resolution No. 28132, authorizing the Chief Executive Officer, LAWA, or designee, to execute said First Amendment to Concession Agreement No. LAA-9173 with Lenlyn Limited dba ICE Currency Services USA. Fiscal Impact Statement: The City Administrative Officer reports that approval of the proposed First Amendment to Concession Agreement No. LAA-9173 with Lenlyn Limited dba ICE Currency Services USA will have no impact on the General Fund. Revenue in the amount of at least $6 million is anticipated to be received during the extended two- year term and deposited under LAWA\u2019s Revenue Code 401070 \u2013 Foreign Exchange & Services. The recommendations in the report comply with the LAWA\u2019s adopted Financial Policies. Community Impact Statement: None submitted TIME LIMIT FILE - SEPTEMBER 12, 2025"
    },
    {
        "item_number": "33",
        "file_number": "15-0694",
        "title": "ADMINISTRATIVE EXEMPTION and TRADE, TRAVEL AND TOURISM COMMITTEE REPORT relative to the Sixth Amendment to Concession Agreement No. LAA-8862 with Boingo Wireless, Inc. covering wireless service at Los Angeles International Airport (LAX).",
        "description": "Recommendations for Council action: 1. CONCUR with the determination by the Board of Airport Commissioners (BOAC) that this action is administratively exempt from the California Environmental Quality Act (CEQA) pursuant to Article II, Section 2(f) of the Los Angeles City CEQA Guidelines. 2. APPROVE the Sixth Amendment to Concession Agreement No. LAA-8862 between Los Angeles World Airports (LAWA) and Boingo Wireless, Inc. to extend the term through June 30, 2026, covering wireless service at LAX. 3. CONCUR with the BOAC\u2019s action on June 5, 2025, by Resolution No. 28181, authorizing the Chief Executive Officer, LAWA, or designee, to execute said Sixth Amendment to Concession Agreement No. LAA-8862 with Boingo Wireless, Inc. Fiscal Impact Statement: The City Administrative Officer reports that approval of the proposed Sixth Amendment to Concession Agreement No. LAA-8862 with Boingo Wireless, Inc., for management and operation of the wireless network in all terminals at LAX will have no impact on the City\u2019s General Fund. Revenue in the amount of $1,400,000 is anticipated to be collected over the 12-month term includes a base annual fee ($583,000) and 50 percent of gross revenues of approximately $1,400,000 (anticipated to be $817,000). The base annual fee is subject to yearly rate escalations triggered by annual Consumer Price Index adjustments effective July 1st of each year. Revenues collected during the lease term will be allocated to the LAWA Revenue Fund. The recommendations in the report comply with the LAWA\u2019s adopted Financial Policies. Community Impact Statement: None submitted TIME LIMIT FILE - SEPTEMBER 12, 2025"
    },
    {
        "item_number": "34",
        "file_number": "25-0733",
        "title": "CDs 6, 11 TRADE, TRAVEL AND TOURISM COMMITTEE REPORT relative to protocols, policies, and procedures for requests by Immigration and Customs Enforcement (ICE) and other federal agents on City-owned airport property.",
        "description": "Recommendations for Council action, pursuant to Motion (Padilla \u2013 Park): 1. REQUEST the Los Angeles Word Airports (LAWA) to provide a verbal report to the full City Council, in closed session if necessary, within seven days, addressing the following: a. Alignment with City Attorney Guidance i. Procedures for areas not open to the general public"
    },
    {
        "item_number": "35",
        "file_number": "25-0811",
        "title": "CATEGORICAL EXEMPTION FROM THE CALIFORNIA ENVIRONMENTAL QUALITY ACT (CEQA) PURSUANT TO CEQA GUIDELINES, AND RELATED CEQA FINDINGS; COMMUNICATION FROM THE LOS ANGELES CITY PLANNING COMMISSION",
        "description": ""
    },
    {
        "item_number": "36",
        "file_number": "25-0781",
        "title": "CD 15 COMMUNICATION FROM THE PORT OF LOS ANGELES (POLA) and CONSIDERATION OF CALIFORNIA ENVIRONMENTAL QUALITY ACT (CEQA) SECTION 21151(C) APPEAL filed by UNITE HERE Local 11 of the action taken by the Board of Harbor Commissioners (BOHC) at its meeting held June 26, 2025, approving the Subsequent Environmental Impact Report (SEIR) for the West Harbor Modification project.",
        "description": ""
    },
    {
        "item_number": "37",
        "file_number": "25-0720",
        "title": "GOVERNMENT OPERATIONS and BUDGET AND FINANCE COMMITTEES\u2019 REPORT relative to the impacts of Cannabis taxation.",
        "description": "Recommendations for Council action, as initiated by Motion (Padilla \u2013 Yaroslavsky): 1. INSTRUCT the City Administrative Officer (CAO) to report to Council with an analysis relative to the revenue impacts of the 19 percent California cannabis excise tax that will come to effect on July 1, 2025. 2. INSTRUCT the CAO to identify funds and issue a solicitation seeking an outside economic analysis of the potential economic impacts of lowering the City's cannabis tax rate to 1.5 percent, 3 percent, 5 percent, and 8 percent. 3. INSTRUCT the CAO and REQUEST the City Attorney to report to Council on the feasibility of instituting a cannabis tax policy that is structured like that of the City of Oakland. 4. DIRECT that the Cannabis Regulation Commission report dated July 18, 2025, attached to Council file No. 25-0720, be transferred to a new Council file. Fiscal Impact Statement: None submitted by the Cannabis Regulation Commission. Neither the CAO nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted."
    },
    {
        "item_number": "38",
        "file_number": "25-0753",
        "title": "PLANNING AND LAND USE MANAGEMENT COMMITTEE REPORT relative to a requested ordinance to implement Assembly Bill (AB) 1033 (Ting, Chapter 752, Statutes of 2023).",
        "description": "Recommendation for Council action, pursuant to Motion (Raman - Blumenfield): INSTRUCT the Department of City Planning, with the assistance of the City Attorney, to prepare and present an ordinance to implement AB 1033 (Ting, Chapter 752, Statutes of 2023), which authorizes local agencies to adopt a local ordinance to allow accessory dwelling units (ADUs) to be sold separately or conveyed from the primary residence as condominiums. Fiscal Impact Statement: Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: Yes For: Los Feliz Neighborhood Council Palms Neighborhood Council Against: Sunland-Tujunga Neighborhood Council Items for which Public Hearings Have Not Been Held - (10 Votes Required for Consideration)"
    },
    {
        "item_number": "39",
        "file_number": "25-1031",
        "title": "MOTION (LEE - HUTT) relative to funding for the installation of signage in Council District 12.",
        "description": "Recommendations for Council action, SUBJECT TO THE APPROVAL OF THE MAYOR: 1. TRANSFER AND APPROPRIATE $7,536.09 from the AB1290 Fund No. 53P, Account No. 281212 (CD 12 Redevelopment Projects - Services) to the Department of Transportation Fund No.100/94, Account No. 003040 (Contractual Services), for installation of signage. 2. AUTHORIZE the City Clerk and/or the Department of Transportation to make any corrections, clarifications, or revisions to the above fund transfer instructions, including any new instructions, in order to effectuate the intent of this Motion, and including any corrections and changes to fund or account numbers; said corrections/clarifications/changes may be made orally, electronically, or by any other means."
    },
    {
        "item_number": "40",
        "file_number": "25-0030",
        "title": "RESOLUTION (HARRIS-DAWSON - BLUMENFIELD) relative to the Declaration of Local Emergency by the Mayor dated January 7, 2025, and Updated Declaration of Local Emergency by the Mayor dated January 13, 2025, due to the windstorm and extreme fire weather system and devastating wildfires in the City of Los Angeles (City), pursuant to Los Angeles Administrative Code (LAAC) Section 8.27.",
        "description": "Recommendation for Council action: ADOPT the accompanying RESOLUTION, dated January 14, 2025, to: 1. Resolve that a local emergency exists resulting from ongoing windstorm and extreme fire weather system and the devastating wildfires in the City within the meaning of LAAC Section 8.21, et seq., as set forth in the Mayor\u2019s January 13, 2025 Updated Declaration of Local Emergency, which incorporated the declaration of emergency dated January 7, 2025, which the City Council hereby ratifies. 2. Resolve that because the local emergency, which began on January 7, 2025, continues to exist, there is a need to continue the state of local emergency, which the City Council hereby ratifies. 3. Instruct and request all appropriate City departments (including proprietary departments), agencies, and personnel, in accordance with LAAC Code Section 8.21 et seq., to continue to perform all duties and responsibilities to represent the City in this matter to respond to and abate the emergency and prevent further harm to the life, health, property, and safety, and receive, process; and, coordinate all inquiries and requirements necessary to obtain whatever State and Federal assistance that may become available to the City and/or to the citizens of the City who may be affected by the emergency. 4. Instruct the General Manager, Emergency Management Department, to advise the Mayor and City Council on the need to extend the state of local emergency, as appropriate. 5. Resolve that, to the extent the public interest and necessity demand the immediate expenditure of public funds to safeguard life, health, or property in response to the local emergency and to support the emergency operations of the City and its departments (including its proprietary departments), agencies, and personnel (including mutual aid resources) in responding to the declared local emergency, the competitive bidding requirements enumerated in City Charter Section 371, and further codified in the LAAC, including LAAC Section 10.15 be suspended until termination of the state of emergency and solely with respect to purchases and contracts needed to respond to the declared state of emergency. 6. Direct and request City departments and agencies making purchases pursuant to the authority granted in paragraph five"
    }
] $$::jsonb
  ) AS j
)
INSERT INTO public."AgendaItems"
  ("MeetingID","Title","Description","ItemNumber","OrderNumber","FileNumber")
SELECT
  (SELECT mid FROM m),
  s.title,
  s.description,
  s.item_number,
  s.item_number,
  s.file_number
FROM src s;

-- Insert agenda items for Sep 12, 2025
WITH m AS (
  SELECT "MeetingID" AS mid FROM public."Meetings" WHERE "Date" = '2025-09-12'
),
src AS (
  SELECT
    (j->>'item_number')::int            AS item_number,
    j->>'file_number'                   AS file_number,
    j->>'title'                         AS title,
    COALESCE(j->>'description','')      AS description
  FROM jsonb_array_elements(
    $$ [
    {
        "item_number": "1",
        "file_number": "22-0403-S3",
        "title": "HOUSING AND HOMELESSNESS and PLANNING AND LAND USE MANAGEMENT COMMITTEES\u2019 REPORT relative to the 2024 Annual Progress Reports on implementation of the General Plan and the Housing Element.",
        "description": "Recommendation for Council action: RECEIVE and FILE the Department of City Planning report dated May 15, 2025, attached to Council file No. 22-0403-S3, relative to the 2024 Annual Progress Reports on implementation of the General Plan and the Housing Element. Fiscal Impact Statement: Not applicable Community Impact Statement: None submitted"
    },
    {
        "item_number": "2",
        "file_number": "23-1106",
        "title": "PUBLIC SAFETY COMMITTEE REPORT relative to a Fire Service Nexus Study regarding new development and population growth within the City, and increased demand for fire services provided by the Los Angeles Fire Department (LAFD).",
        "description": "Recommendation for Council action: NOTE and FILE the LAFD report dated July 9, 2025, attached to the Council file, relative to a Fire Service Nexus Study to evaluate the relationship between new development and population growth within the City of Los Angeles and increased demand for fire services currently provided by the LAFD. Fiscal Impact Statement: Not applicable Community Impact Statement: None submitted"
    },
    {
        "item_number": "3",
        "file_number": "25-0876",
        "title": "TRADE, TRAVEL AND TOURISM COMMITTEE REPORT relative to the Los Angeles World Airports (LAWA) Fiscal Year 2025-26 Statement of Debt Accountability and Capital Improvement Plan.",
        "description": "Recommendation for Council action: APPROVE the LAWA Fiscal Year 2025-26 Statement of Debt Accountability and Capital Improvement Plan. Fiscal Impact Statement: None submitted by the LAWA. Neither the City Administrative Officer nor the Chief Legislative Analyst has completed a financial analysis of this report. Community Impact Statement: None submitted"
    },
    {
        "item_number": "4",
        "file_number": "25-0532",
        "title": "COMMUNICATIONS FROM THE CITY ADMINISTRATIVE OFFICER AND THE DEPARTMENT OF CITY PLANNING relative to authorization for the Local Coastal Program Local Assistance Grant award acceptance and agreement execution.",
        "description": ""
    },
    {
        "item_number": "5",
        "file_number": "25-0885",
        "title": "CIVIL RIGHTS, EQUITY, IMMIGRATION AGING AND DISABILITY and BUDGET AND FINANCE COMMITTEES\u2019 REPORT relative to a report on all City projects, programs, and services that could be impacted by H.R. 1 (One Big Beautiful Bill Act); and related matters.",
        "description": "Recommendation for Council action, pursuant to Motion (Raman - Yaroslavsky): INSTRUCT the City Administrative Officer (CAO), with the assistance of the Chief Legislative Analyst (CLA) and relevant departments, to report to Council on all City projects, programs, and services that could be impacted by H.R. 1 (One Big Beautiful Bill Act), including estimates on the potential fiscal impacts of reduced grant funding that the City receives from the federal government. Fiscal Impact Statement: Neither the CAO nor the CLA has completed a financial analysis of this report. Community Impact Statement: None submitted Items Called Special Motions for Posting and Referral Council Members' Requests for Excuse from Attendance at Council Meetings Adjourning Motions Council Adjournment EXHAUSTION OF ADMINISTRATIVE REMEDIES - If you challenge a City action in court, you may be limited to raising only those issues you or someone else raised at the public hearing described in this notice, or in written correspondence delivered to the City Clerk at or prior to, the public hearing. Any written correspondence delivered to the City Clerk before the City Council's final action on a matter will become a part of the administrative record. CODE OF CIVIL PROCEDURE SECTION 1094.5 - If a Council action is subject to judicial challenge pursuant to Code of Civil Procedure Section 1094.5, be advised that the time to file a lawsuit challenging a final action by the City Council is limited by Code of Civil Procedure Section 1094.6 which provides that the lawsuit must be filed no later than the 90th day following the date on which the Council's action becomes final. Materials relative to items on this agenda can be obtained from the Office of the City Clerk's Council File Management System, at lacouncilfile.com by entering the Council File number listed immediately following the item number (e.g., 00-0000)."
    }
] $$::jsonb
  ) AS j
)
INSERT INTO public."AgendaItems"
  ("MeetingID","Title","Description","ItemNumber","OrderNumber","FileNumber")
SELECT
  (SELECT mid FROM m),
  s.title,
  s.description,
  s.item_number,
  s.item_number,
  s.file_number
FROM src s;

-- Insert summaries for Sep 9, 2025
WITH m AS (
  SELECT "MeetingID" AS mid FROM public."Meetings" WHERE "Date" = '2025-09-09'
),
src AS (
  SELECT
    (j->>'StartTime')                     AS StartTime,
    j->>'Title'                           AS Title,
    j->>'Summary'                         AS Summary
  FROM jsonb_array_elements(
    $$  [
        {
            "StartTime": "01:04:29,761",
            "Title": "Faith Community Leaders Support Historic Wage Increase and Rent Control",
            "Summary": "Father Mark Hallahan and representatives from the faith community praise the historic wage increase and express support for rent control measures, highlighting the importance of fair wages and affordable housing for low-income families."
        },
        {
            "StartTime": "00:57:11,127",
            "Title": "City Council Meeting - Public Comment Session",
            "Summary": "The public comment session is being held where residents can voice their concerns and speak on various items on the agenda, including a proposal to keep pools open on weekends, a motion to investigate corruption among city officials, and others."
        },
        {
            "StartTime": "01:15:49,695",
            "Title": "Protester Discusses LAPD Violence Against Peaceful Demonstrators",
            "Summary": "A protester discusses how the LAPD has been using racial slurs and disrupting meetings, while also highlighting instances of violence against peaceful protesters, including a man losing his finger. The speaker criticizes some City Council members for voting in favor of allocating $17.3 million for LAPD overtime despite the harm caused to protesters."
        },
        {
            "StartTime": "01:25:48",
            "Title": "Council Discussion on Immigration Raids",
            "Summary": "The speakers discuss the impact of recent immigration raids, particularly in their district, and call for the city to take action to protect residents' safety and address the root causes of these issues. They also express concern over the Supreme Court's decision and its implications for the country."
        },
        {
            "StartTime": "01:18:06,371",
            "Title": "UCLA Students Fight for Fair Olympic Wages",
            "Summary": "The Undergraduate Student Association Council at UCLA discusses the economic injustices faced by student workers and their families, advocating for a $30 Olympic wage and fair treatment during the 2020 Olympics."
        },
        {
            "StartTime": "00:44:53,417",
            "Title": "Council Meeting Discussion on Budget and Finance Committee Items",
            "Summary": "The council discusses and votes on budget and finance committee items, including those considered during the closed session. They also review and approve previously approved items and consider a special amendment to item 8."
        },
        {
            "StartTime": "01:02:32,052",
            "Title": "Immigration Reform Discussion at Town Hall Meeting",
            "Summary": "In a town hall meeting discussion, Speaker 15 proposes an idea for immigration reform, suggesting selling visas to undocumented immigrants and legal residents at a graduated price based on years of residency. The proposal aims to incentivize those who genuinely want to stay in the country and contribute positively, rather than those chasing \"quick fixes.\" Other speakers express support for workers' rights and urge council members to implement living wage ordinances."
        },
        {
            "StartTime": "01:09:08,983",
            "Title": "Olympic Wage Discussion",
            "Summary": "SRT speakers discuss the implementation of an Olympic wage, which would benefit them financially, allowing them to continue living in Los Angeles. They also express gratitude for support and hope that companies will pay what they owe them."
        },
        {
            "StartTime": "00:53:19,866",
            "Title": "LA Tourism Worker Wage Referendum Delay Sparks Concerns Over Public Trust and Police Accountability",
            "Summary": "A coalition partner of the LA Alliance for Tourism, Jobs and Progress expresses concerns over the delay in verifying signatures for a tourism worker wage referendum, which they claim broke public trust. The speaker also criticizes the police department's handling of allegations of extortion and refusal to make records, calling for oversight and investigation from the National Guard."
        },
        {
            "StartTime": "01:12:17,193",
            "Title": "Border Security Debate",
            "Summary": "A debate about border security and law enforcement operations is taking place, with speakers discussing their plans to address issues such as gang violence and looting in Los Angeles, and calling for the re-election of council member Spindler."
        }
    ]$$::jsonb
  ) AS j
)
INSERT INTO public."Summaries"
  ("MeetingID","StartTime","Title","Summary")
SELECT
  (SELECT mid FROM m),
  s.StartTime,
  s.Title,
  s.Summary
FROM src s;

-- Insert summaries for Sep 10, 2025
WITH m AS (
  SELECT "MeetingID" AS mid FROM public."Meetings" WHERE "Date" = '2025-09-10'
),
src AS (
  SELECT
    (j->>'StartTime')                     AS StartTime,
    j->>'Title'                           AS Title,
    j->>'Summary'                         AS Summary
  FROM jsonb_array_elements(
    $$  [
        {
            "StartTime": "01:53:14,373",
            "Title": "Council Meeting Agenda Item Discussion",
            "Summary": "The council members discuss and vote on several agenda items, including a roll call vote on item 29, a reconsideration of item 41 for public comment, and an item for which to be sent forth with urgency."
        },
        {
            "StartTime": "01:35:35,442",
            "Title": "Housing Committee Discussion on Tenants' Rights and Rent Reductions",
            "Summary": "The discussion focuses on tenants' rights in Los Angeles, particularly the need for rent reductions when property owners fail to make necessary repairs. Speakers from ACE and the housing committee share their perspectives on improving SEP (Section 8 Program) and ensuring quality repairs."
        },
        {
            "StartTime": "01:32:40,434",
            "Title": "Tenants Discuss Housing Issues and Request Justice",
            "Summary": "A group of tenants speak out about their poor living conditions and demand justice from the housing department, advocating for policy changes and recommendations to address their concerns, including a petition to prevent landlords from increasing rent without making necessary repairs."
        },
        {
            "StartTime": "01:22:12,158",
            "Title": "Rent Control Discussion at Public Hearing",
            "Summary": "Speakers discuss the need for rent control and affordable housing, citing economic difficulties and personal struggles with high rent costs. They advocate for regulations to cap rent at 3% and improve transparency in repairs, as well as support for low-income families affected by rising rents."
        },
        {
            "StartTime": "01:19:59,921",
            "Title": "Rent Increases and Housing Issues",
            "Summary": "The discussion revolves around rent increases and housing issues in the community, with speakers discussing their experiences with landlords and advocating for rent stabilization. They also address the 03% LARSO-LA rent stabilization formula and its impact on small landlords."
        },
        {
            "StartTime": "01:14:09,567",
            "Title": "Support for West Harbor Modification Project in San Pedro",
            "Summary": "The discussion revolves around supporting the West Harbor Modification Project in San Pedro, with speaker Andrew Silber advocating for its approval and certification of the Supplemental Environmental Impact Report, highlighting his personal connection to the community and the need for this project to fulfill the potential of San Pedro."
        },
        {
            "StartTime": "01:08:49,774",
            "Title": "Opposition to Port Development Appeal",
            "Summary": "A speaker from the Los Angeles Maritime Institute opposes an appeal to a port development decision, citing concerns about the process and its impact on the community. He urges the council to uphold the original decision and deny the appeal."
        },
        {
            "StartTime": "00:55:25,668",
            "Title": "City Council Meeting on West Harbor Modification Project",
            "Summary": "The city council is discussing the approval of the West Harbor Modification Project by the Los Angeles Board of Harbor Commissioners. Speaker_62 expresses gratitude for the support and calls for public commenting on specific items."
        },
        {
            "StartTime": "00:51:47,377",
            "Title": "Los Angeles City Council Discussion on Community Events and Park Space",
            "Summary": "The Los Angeles City Council discusses the importance of community-driven organizations, the need for more park space in San Pedro downtown, and the implementation of the Secure Tenant Eviction Protection (SCEP) plan."
        },
        {
            "StartTime": "00:44:30,517",
            "Title": "Tenants' Rights Discussion at City Council Meeting",
            "Summary": "The discussion focuses on tenants' rights in Los Angeles, with attendees sharing their experiences and advocating for improvements to the city's housing policies. They specifically discuss the need for a clear path to activating habitability plans and express gratitude towards council members who have supported tenant rights initiatives."
        },
        {
            "StartTime": "01:49:03,090",
            "Title": "City Council Meeting Debate on Election Integrity",
            "Summary": "The discussion revolves around concerns about election integrity and the threat of autocratic regimes undermining democracy. Speaker 37 presents a resolution aimed at stopping administrative actions to rig elections and maintain California's commitment to democracy."
        },
        {
            "StartTime": "00:39:12,760",
            "Title": "Council Meeting Discussion on Voting Items and Public Comment",
            "Summary": "The council members discuss voting items, including some being moved to later dates or made special, and plan for public comment at 11 o'clock with an estimated time limit for speakers."
        }
    ]$$::jsonb
  ) AS j
)
INSERT INTO public."Summaries"
  ("MeetingID","StartTime","Title","Summary")
SELECT
  (SELECT mid FROM m),
  s.StartTime,
  s.Title,
  s.Summary
FROM src s;


-- Insert summaries for Sep 12, 2025
WITH m AS (
  SELECT "MeetingID" AS mid FROM public."Meetings" WHERE "Date" = '2025-09-12'
),
src AS (
  SELECT
    (j->>'StartTime')                     AS StartTime,
    j->>'Title'                           AS Title,
    j->>'Summary'                         AS Summary
  FROM jsonb_array_elements(
    $$ [
        {
            "StartTime": "01:09:11,500",
            "Title": "Honoring a Community Leader",
            "Summary": "The discussion revolves around honoring Veronica, a community leader who has been serving the area for 21 years, and her impact on improving people's lives through her work and policies."
        },
        {
            "StartTime": "00:54:14,813",
            "Title": "World Cup Walking Soccer Launch",
            "Summary": "SRT speaker discusses the launch of a walking soccer program before the World Cup in Los Angeles, expressing gratitude to Jeremy and other supporters for their help. The conversation includes thank-yous to volunteers, players, and city officials."
        },
        {
            "StartTime": "00:43:02,800",
            "Title": "Los Angeles City Council Meeting Agenda Discussion",
            "Summary": "The Los Angeles City Council discusses their agenda, including public comments, approval of minutes, commendatory resolutions, and presentations from various council districts. They also address items for special consideration and open the floor for discussion."
        },
        {
            "StartTime": "00:04:02,437",
            "Title": "Homelessness Solutions in LA",
            "Summary": "The discussion focuses on homelessness solutions in Los Angeles, with speakers from the Housing Authority and local organizations sharing their experiences and efforts to provide affordable housing and support services. They highlight the importance of partnerships and community engagement in addressing this issue."
        },
        {
            "StartTime": "02:28:19,617",
            "Title": "City Officials Under Fire for Clowns in Charge",
            "Summary": "A public speaker criticizes city officials and clowns for their incompetence, citing examples of budget mismanagement, lack of action on pressing issues like homelessness and fires, and poor planning."
        },
        {
            "StartTime": "02:30:19,562",
            "Title": "LA City Council Discussion on Voting Systems",
            "Summary": "The Los Angeles City Council discussed various voting systems, including star voting, rank choice voting, and the current top two system. Speakers shared their experiences with different voting methods and emphasized the importance of electoral accuracy. Dr. Sam Davidson presented research findings from Harvard and UC Berkeley that suggest star voting produces the most accurate elections."
        },
        {
            "StartTime": "02:24:21,985",
            "Title": "Council Discussion on Senior Parking and Police Oversight",
            "Summary": "The speakers discuss the need for restrictive parking to prevent seniors from having to clean up after others, as well as their concerns about police oversight and the lack of ability for general public comments in certain situations."
        },
        {
            "StartTime": "00:00:00,031",
            "Title": "Community Policing and Immigration Policy",
            "Summary": "Law enforcement officials discuss their efforts to engage with the community and dispel myths about police department policies on immigration. They highlight events like \"Coffee with a Cop\" as opportunities for dialogue and networking. The conversation also touches on the impact of immigration policies on local businesses and residents."
        },
        {
            "StartTime": "02:16:39,145",
            "Title": "Council Discussion on Public Participation and Agenda Items",
            "Summary": "The council discusses the lack of public participation in agenda items due to previous committee votes, leading to some members not being aware of the full scope of issues. Speaker 28 expresses frustration with the system, while Speaker 15 criticizes Nithya Brahmin's handling of homelessness committee matters."
        },
        {
            "StartTime": "02:34:37,834",
            "Title": "City Council Meeting Description",
            "Summary": "Council members discuss the posting of motions and the upcoming Festival of Philippine Arts and Culture in San Pedro. They also address announcements and remove a council member for disrupting the meeting."
        },
        {
            "StartTime": "01:14:00,807",
            "Title": "Veronica's Tribute to the Beloved Community of Watts",
            "Summary": "In this emotional exchange, Veronica expresses gratitude to Councilmember McCosker for his great work in her community, highlighting the importance of acknowledging and supporting vulnerable populations within the community."
        },
        {
            "StartTime": "02:20:50,878",
            "Title": "LA City Council Discussion on Voting Systems",
            "Summary": "The Los Angeles City Council discussed various voting systems, including star voting, rank choice voting, and the current top two system. Speakers shared their experiences with different voting methods and emphasized the importance of electoral accuracy. Dr. Sam Davidson presented research findings from Harvard and UC Berkeley that suggest star voting produces the most accurate elections."
        },
        {
            "StartTime": "02:32:51,493",
            "Title": "Meeting Disruptions and Citizenship Plan Discussion",
            "Summary": "The discussion revolves around a citizen's plan to obtain citizenship through a tax plan, with multiple speakers presenting their views and concerns. One speaker receives a time limit warning for disrupting the meeting, while another attempts to address chain of command issues within the building."
        },
        {
            "StartTime": "01:31:09,919",
            "Title": "Celebration of Latino Hispanic Heritage Month",
            "Summary": "The discussion focuses on celebrating Latino Hispanic Heritage Month in the City of Los Angeles, with a presentation honoring a family who has made an empire while preserving their traditions from Mexico."
        }
    ] $$::jsonb
  ) AS j
)
INSERT INTO public."Summaries"
  ("MeetingID","StartTime","Title","Summary")
SELECT
  (SELECT mid FROM m),
  s.StartTime,
  s.Title,
  s.Summary
FROM src s;


COMMIT;