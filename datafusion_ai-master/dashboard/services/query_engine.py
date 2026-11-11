from django.db import connection


def dict_fetchall(cursor):
    """Return all rows from a cursor as a list of dicts."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_kpi_summary():
    """
    Returns the 4 main KPI cards:
    Total Revenue, Total Customers, Average ARPU, Total Sales Count
    """
    kpis = {
        'total_revenue'   : 0,
        'total_customers' : 0,
        'avg_arpu'        : 0,
        'total_sales'     : 0,
        'total_leads'     : 0,
        'conversion_rate' : 0,
    }

    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT COALESCE(SUM(totalrevenue_jod), 0) FROM etl_sale"
            )
            kpis['total_revenue'] = round(
                float(cursor.fetchone()[0] or 0), 2
            )
        except Exception:
            pass

        try:
            cursor.execute("SELECT COUNT(*) FROM etl_customer")
            kpis['total_customers'] = int(cursor.fetchone()[0] or 0)
        except Exception:
            pass

        try:
            cursor.execute(
                "SELECT COALESCE(AVG(monthlyarpu_jod), 0) FROM etl_customer"
            )
            kpis['avg_arpu'] = round(
                float(cursor.fetchone()[0] or 0), 2
            )
        except Exception:
            pass

        try:
            cursor.execute("SELECT COUNT(*) FROM etl_sale")
            kpis['total_sales'] = int(cursor.fetchone()[0] or 0)
        except Exception:
            pass

        # Total leads
        try:
            cursor.execute("SELECT COUNT(*) FROM etl_lead")
            kpis['total_leads'] = int(cursor.fetchone()[0] or 0)
        except Exception:
            pass

        try:
            cursor.execute(
                "SELECT COUNT(*) FROM etl_lead WHERE leadstage = 'Won'"
            )
            won = int(cursor.fetchone()[0] or 0)
            if kpis['total_leads'] > 0:
                kpis['conversion_rate'] = round(
                    won / kpis['total_leads'] * 100, 1
                )
        except Exception:
            pass

    return kpis


def get_revenue_by_month():
    """
    Returns monthly revenue for the line chart.
    { labels: [...], data: [...] }
    """
    labels = []
    data   = []

    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT
                    SUBSTR(saledate, 1, 7)   AS month,
                    ROUND(SUM(totalrevenue_jod), 2) AS revenue
                FROM etl_sale
                WHERE saledate IS NOT NULL
                  AND saledate != ''
                GROUP BY SUBSTR(saledate, 1, 7)
                ORDER BY month ASC
                LIMIT 24
            """)
            rows = cursor.fetchall()
            for row in rows:
                labels.append(str(row[0]))
                data.append(float(row[1] or 0))
        except Exception:
            pass

    return {'labels': labels, 'data': data}


def get_customers_by_segment():
    """
    Returns customer count per segment for the pie chart.
    { labels: [...], data: [...] }
    """
    labels = []
    data   = []

    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT
                    segment,
                    COUNT(*) AS total
                FROM etl_customer
                WHERE segment IS NOT NULL
                  AND segment != ''
                GROUP BY segment
                ORDER BY total DESC
            """)
            rows = cursor.fetchall()
            for row in rows:
                labels.append(str(row[0]))
                data.append(int(row[1] or 0))
        except Exception:
            pass

    return {'labels': labels, 'data': data}


def get_top_campaigns():
    """
    Returns top 8 campaigns by revenue for the bar chart.
    { labels: [...], data: [...] }
    """
    labels = []
    data   = []

    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT
                    campaignname,
                    ROUND(revenue_generated, 2) AS revenue
                FROM etl_campaign
                WHERE revenue_generated IS NOT NULL
                ORDER BY revenue_generated DESC
                LIMIT 8
            """)
            rows = cursor.fetchall()
            for row in rows:
                labels.append(str(row[0])[:30])
                data.append(float(row[1] or 0))
        except Exception:
            pass

    return {'labels': labels, 'data': data}


def get_sales_by_channel():
    """
    Returns sales count by channel for a doughnut chart.
    { labels: [...], data: [...] }
    """
    labels = []
    data   = []

    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT
                    channel,
                    COUNT(*) AS total
                FROM etl_sale
                WHERE channel IS NOT NULL
                  AND channel != ''
                GROUP BY channel
                ORDER BY total DESC
            """)
            rows = cursor.fetchall()
            for row in rows:
                labels.append(str(row[0]))
                data.append(int(row[1] or 0))
        except Exception:
            pass

    return {'labels': labels, 'data': data}


def get_leads_by_stage():
    """
    Returns lead count by stage for a horizontal bar chart.
    { labels: [...], data: [...] }
    """
    labels = []
    data   = []

    with connection.cursor() as cursor:
        try:
            cursor.execute("""
                SELECT
                    leadstage,
                    COUNT(*) AS total
                FROM etl_lead
                WHERE leadstage IS NOT NULL
                  AND leadstage != ''
                GROUP BY leadstage
                ORDER BY total DESC
            """)
            rows = cursor.fetchall()
            for row in rows:
                labels.append(str(row[0]))
                data.append(int(row[1] or 0))
        except Exception:
            pass

    return {'labels': labels, 'data': data}

def get_analytics_summary():
    """Quick behavior stats for the dashboard summary row."""
    result = {
        'total_visits'  : 0,
        'total_sessions': 0,
        'active_users'  : 0,
    }
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT COUNT(*) FROM core_pagevisit")
            result['total_visits'] = int(cursor.fetchone()[0] or 0)
        except Exception:
            pass
        try:
            cursor.execute("SELECT COUNT(*) FROM core_usersession")
            result['total_sessions'] = int(cursor.fetchone()[0] or 0)
        except Exception:
            pass
        try:
            cursor.execute(
                "SELECT COUNT(DISTINCT user_id) FROM core_pagevisit "
                "WHERE user_id IS NOT NULL"
            )
            result['active_users'] = int(cursor.fetchone()[0] or 0)
        except Exception:
            pass
    return result