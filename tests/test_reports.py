def test_reports_list(client, auth_headers):
    resp = client.get("/reports/")
    assert resp.status_code == 200
    assert b"Reports" in resp.data


def test_generate_report_page(client, auth_headers):
    resp = client.get("/reports/generate")
    assert resp.status_code == 200
    assert b"Generate Report" in resp.data


def test_generate_report_with_articles(client, auth_headers, db, sample_article):
    resp = client.post("/reports/generate", data={
        "article_ids": [str(sample_article.id)],
        "report_type": "general",
        "title": "Test Report",
    }, follow_redirects=True)
    assert resp.status_code in (200, 302)
    if resp.status_code == 200:
        assert b"Test Report" in resp.data or b"generated" in resp.data


def test_report_detail(client, auth_headers, db):
    from src.news_app.models.report import Report
    report = Report(
        user_id=1,
        title="Sample Report",
        report_type="general",
        status="completed",
        summary="A test report",
    )
    db.session.add(report)
    db.session.commit()

    resp = client.get(f"/reports/{report.id}")
    assert resp.status_code == 200


def test_delete_report(client, auth_headers, db):
    from src.news_app.models.report import Report
    report = Report(
        user_id=1,
        title="To Delete",
        report_type="general",
        status="draft",
    )
    db.session.add(report)
    db.session.commit()

    resp = client.post(f"/reports/delete/{report.id}", follow_redirects=True)
    assert resp.status_code == 200
