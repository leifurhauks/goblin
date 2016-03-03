import asyncio
import datetime

from pytz import utc

from tornado.platform.asyncio import AsyncIOMainLoop

from mogwai import properties
from mogwai.connection import setup, close_global_pool
from mogwai.models import Vertex, Edge, V
from mogwai.relationships import Relationship


class WorksFor(Edge):
    start_date = properties.DateTime()


class MemberOf(Edge):
    since = properties.DateTime()


class BelongsTo(Edge):
    pass


class Organization(Vertex):
    name = properties.String()
    email = properties.Email()
    url = properties.URL()


class Department(Vertex):
    name = properties.String()
    email = properties.Email()
    url = properties.URL()
    belongs_to = Relationship(BelongsTo, Organization)


class Person(Vertex):
    name = properties.String()
    email = properties.Email()
    url = properties.URL()
    works_for = Relationship(WorksFor, Organization)
    member_of = Relationship(MemberOf, Department)


async def main():
    # Star by creating a graph.

    # First create some nodes
    zfail = await Organization.create(
        name="zfail", email="zfail@zfail.com", url="https://zfail.com")
    west = await Organization.create(
        name="west", email="west@west.com", url="https://west.com")

    r_and_d = await Department.create(
        name="r_and_d", email="randd@somemail.com", url="https://randd.com")
    c_and_p = await Department.create(
        name="c_and_p", email="candp@somemail.com", url="https://candp.com")

    jon = await Person.create(
        name="jon", email="jon@jon.com", url="https://jon.com/")
    dave = await Person.create(
        name="dave", email="dave@dave.com", url="https://dave.com/")
    leif = await Person.create(
        name="leif", email="leif@leif.com", url="https://leif.com/")

    # Create some edges
    r_and_d_belongs_to = await BelongsTo.create(r_and_d, zfail)
    c_and_p_belongs_to = await BelongsTo.create(c_and_p, west)

    jon_works_for = await WorksFor.create(
        jon, zfail, start_date=datetime.datetime(2014, 1, 1, tzinfo=utc))
    jon_member_of = await MemberOf.create(
        jon, r_and_d, since=datetime.datetime(2014, 1, 1, tzinfo=utc))

    leif_works_for = await WorksFor.create(
        leif, zfail, start_date=datetime.datetime(2014, 1, 1, tzinfo=utc))
    leif_member_of = await MemberOf.create(
        leif, r_and_d, since=datetime.datetime(2014, 1, 1, tzinfo=utc))

    dave_works_for = await WorksFor.create(
        dave, west, start_date=datetime.datetime(2014, 1, 1, tzinfo=utc))
    dave_member_of = await MemberOf.create(
        dave, c_and_p, since=datetime.datetime(2014, 1, 1, tzinfo=utc))

    # You can also create nodes and edges at the same time
    # using the relationship properties
    dave_member_of_dep, a_and_h = await dave.member_of.create(
        edge_params={"since": datetime.datetime(2014, 1, 1, tzinfo=utc)},
        vertex_params={"name": "a_and_h", "email": "aandh@somemail.com",
                       "url": "https://aandh.com"})

    try:
        # Ok, now lets try out some of the Vertex methods these methods,
        # like all query methods return a gremlinclient.Stream object
        stream = await jon.outV()
        jons_out_v = await stream.read()
        print("These are Jon's neighbours:\n\n{}\n\n{}\n".format(
            jons_out_v[0], jons_out_v[1]))

        stream = await dave.outE()
        daves_out_e = await stream.read()
        print("These are Daves's rels:\n\n{}\n\n{}\n".format(
            daves_out_e[0], daves_out_e[1]))

        # Ok, how about some more complex queries?
        stream = await V(jon).out().in_step().get()
        jons_coworkers = await stream.read()
        print("These are Jons's coworkers:\n\n{}\n".format(
            jons_coworkers[0]))

    # Clean up
    finally:
        await r_and_d_belongs_to.delete()
        await c_and_p_belongs_to.delete()
        await jon_works_for.delete()
        await jon_member_of.delete()
        await leif_works_for.delete()
        await leif_member_of.delete()
        await dave_works_for.delete()
        await dave_member_of.delete()
        await dave_member_of_dep.delete()
        await zfail.delete()
        await west.delete()
        await r_and_d.delete()
        await c_and_p.delete()
        await jon.delete()
        await dave.delete()
        await leif.delete()
        await a_and_h.delete()


if __name__ == "__main__":
    setup("localhost", future=asyncio.Future)
    AsyncIOMainLoop().install()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    close_global_pool()  # maybe this should be teardown
    loop.close()
