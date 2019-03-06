from py2neo import Graph, NodeMatcher, Node, Relationship, RelationshipMatcher
import json
import utils as ut
import uuid


class FanGraph(object):
    """
    This object provides a set of helper methods for creating and retrieving Nodes and relationship from
    a Neo4j database.
    """

    # Connects to the DB and sets a Graph instance variable.
    # Also creates a NodeMatcher, which is a py2neo class.
    def __init__(self,  auth, host, port, secure=False, ):
        self._graph = Graph(secure=secure,
                            bolt=True,
                            auth=auth,
                            host=host,
                            port=port)
        self._node_matcher = NodeMatcher(self._graph)
        self._relationship_matcher = RelationshipMatcher(self._graph)

    def run_match(self, labels=None, properties=None):
        """
        Uses a NodeMatcher to find a node matching a "template."
        :param labels: A list of labels that the node must have.
        :param properties: A parameter list of the form prop1=value1, prop2=value2, ...
        :return: An array of Node objects matching the pattern.
        """
        #ut.debug_message("Labels = ", labels)
        #ut.debug_message("Properties = ", json.dumps(properties))

        if labels is not None and properties is not None:
            result = self._node_matcher.match(labels, **properties)
        elif labels is not None and properties is None:
            result = self._node_matcher.match(labels)
        elif labels is None and properties is not None:
            result = self._node_matcher.match(**properties)
        else:
            raise ValueError("Invalid request. Labels and properties cannot both be None.")

        # Convert NodeMatch data into a simple list of Nodes.
        full_result = []
        for r in result:
            full_result.append(r)

        return full_result

    def find_nodes_by_template(self, tmp):
        """
        :param tmp: A template defining the label and properties for Nodes to return. An
         example is { "label": "Fan", "template" { "last_name": "Ferguson", "first_name": "Donald" }}
        :return: A list of Nodes matching the template.
        """
        labels = tmp.get('label')
        props = tmp.get("template")
        result = self.run_match(labels=labels, properties=props)
        return result

    # Create and save a new node for  a 'Fan.'
    def create_fan(self, uni, last_name, first_name):
        n = Node("Fan", uni=uni, last_name=last_name, first_name=first_name)
        tx = self._graph.begin(autocommit=True)
        tx.create(n)

    # Given a UNI, return the node for the Fan.
    def get_fan(self, uni):
        n = self.find_nodes_by_template({"label": "Fan", "template": {"uni": uni}})
        if n is not None and len(n) > 0:
            n = n[0]
        else:
            n = None

        return n

    def create_player(self, player_id, last_name, first_name):
        n = Node("Player", player_id=player_id, last_name=last_name, first_name=first_name)
        tx = self._graph.begin(autocommit=True)
        tx.create(n)
        return n

    def get_player(self, player_id):
        n = self.find_nodes_by_template({"label": "Player", "template": {"player_id": player_id}})
        if n is not None and len(n) > 0:
            n = n[0]
        else:
            n = None

        return n

    def create_team(self, team_id, team_name):
        n = Node("Team", team_id=team_id, team_name=team_name)
        tx = self._graph.begin(autocommit=True)
        tx.create(n)
        return n

    def get_team(self, team_id):
        n = self.find_nodes_by_template({"label": "Team", "template": {"team_id": team_id}})
        if n is not None and len(n) > 0:
            n = n[0]
        else:
            n = None

        return n

    def create_supports(self, uni, team_id):
        """
        Create a SUPPORTS relationship from a Fan to a Team.
        :param uni: The UNI for a fan.
        :param team_id: An ID for a team.
        :return: The created SUPPORTS relationship from the Fan to the Team
        """
        f = self.get_fan(uni)
        t = self.get_team(team_id)
        r = Relationship(f, "SUPPORTS", t)
        tx = self._graph.begin(autocommit=True)
        tx.create(r)
        return r

    # Create an APPEARED relationship from a player to a Team
    def create_appearance(self, player_id, team_id):
        try:
            f = self.get_player(player_id)
            t = self.get_team(team_id)
            r = Relationship(f, "APPEARED", t)
            tx = self._graph.begin(autocommit=True)
            tx.create(r)
        except Exception as e:
            print("create_appearances: exception = ", e)

    # Create a FOLLOWS relationship from a Fan to another Fan.
    def create_follows(self, follower, followed):
        f = self.get_fan(follower)
        t = self.get_fan(followed)
        r = Relationship(f, "FOLLOWS", t)
        tx = self._graph.begin(autocommit=True)
        tx.create(r)

    def get_comment(self, comment_id):
        n = self.find_nodes_by_template({"label": "Comment", "template": {"comment_id": comment_id}})
        if n is not None and len(n) > 0:
            n = n[0]
        else:
            n = None

        return n

    def create_comment(self, uni, comment, team_id=None, player_id=None):
        """
        Creates a comment
        :param uni: The UNI for the Fan making the comment.
        :param comment: A simple string.
        :param team_id: A valid team ID or None. team_id and player_id cannot BOTH be None.
        :param player_id: A valid player ID or None
        :return: The Node representing the comment.
        """
        f = self.get_fan(uni)
        #print(f["first_name"])
        comment_id = str(uuid.uuid4())
        #print(comment_id)
        n = Node("Comment", comment_id=comment_id, comment=comment)
        tx1 = self._graph.begin(autocommit=True)
        tx1.create(n)


        r1 = Relationship(f, "COMMENT_BY", n)
        print(f["first_name"], n["comment"])
        tx2 = self._graph.begin(autocommit=True)
        tx2.create(r1)

        if team_id:
            t = self.get_team(team_id)
            r2 = Relationship(n, "COMMENT_ON", t)
            tx3 = self._graph.begin(autocommit=True)
            tx3.create(r2)
        if player_id:
            p = self.get_player(player_id)
            r3 = Relationship(n, "COMMENT_ON", p)
            tx4 = self._graph.begin(autocommit=True)
            tx4.create(r3)
        
        
        print("Created comment. COMMENT_ID: ", comment_id, "Comment: ", comment)
        return n


        

    def create_sub_comment(self, uni, origin_comment_id, comment):
        """
        Create a sub-comment (response to a comment or response) and links with parent in thread.
        :param uni: ID of the Fan making the comment.
        :param origin_comment_id: Id of the comment to which this is a response.
        :param comment: Comment string
        :return: Created comment.
        """
        f = self.get_fan(uni)
        c = self.get_comment(origin_comment_id)
        coc_comment_id = str(uuid.uuid4())
        n = Node("Comment", comment_id=coc_comment_id, comment=comment)
        tx1 = self._graph.begin(autocommit=True)
        tx1.create(n)

        tx2 = self._graph.begin(autocommit=True)
        r1 = Relationship(f, "RESPONSE_BY", n)
        tx2.create(r1)
        tx3 = self._graph.begin(autocommit=True)
        r2 = Relationship(n, "RESPONSE_TO", c)
        tx3.create(r2)

        print("Created comment. COC_COMMENT_ID:", coc_comment_id, "Comment:", comment)
        return n


    def get_player_comments(self, player_id):
        #pass
        """
        Gets all of the comments associated with a player, all of the comments on the comment and comments
        on the comments, etc. Also returns the Nodes for people making the comments.
        :param player_id: ID of the player.
        :return: Graph containing comment, comment streams and commenters.
        """
        q = "MATCH (fan: Fan)-[:RESPONSE_BY]->(coc: Comment)-[:RESPONSE_TO*]->(oc: Comment)-[:COMMENT_ON]->(player:Player {player_id: '" + player_id + "'}), (origin_fan: Fan)-[:COMMENT_BY]->(oc: Comment) RETURN coc, oc, fan, origin_fan"
        #query = self._graph.run(q, player_id)
        #results = query.execute(p=player_id)
        #print(results)
        result = self._graph.run(q)
        return result.data()
        #print(result)
        #tx.commit()


        """
        player = self.get_player(player_id) # node param for pealtionship match constructor
        comments = self._relationship_matcher.match((None, player), "COMMENT_ON")
        for c in comments:
            original_comment = c.start_node
            coc = self._relationship_matcher.match([])

        
        for c in comments:
            comments_on_comments = self._relationship_matcher.match([c], "RESPONSE_TO")

        for comment_on_player_rel in self._graph.match(rel_type="COMMENT_ON", end_node=player)
            comment = comment_on_player_rel.start_node()
            for comment_on_comment_rel in self._graph.match(rel_type="RESPONSE_TO", end_node=comment)
        player = self._graph.run("MATCH (coc: Comment)-[:RESPONSE_TO*]->(oc: Comment)-[:COMMENT_ON]->(player:Player {player_id:}")
        #n1 = self.find_nodes_by_template({"label": "Comment", "template": {"player_id": player_id}})
        
        #n2 = self.find_nodes_by_template({"label": "Comment", "template": {"comment_id": player_id}})

        #q1 = "match C = (n:Comment)-[r:COMMENT_ON]->(m:Player {player_id: player_id}) return n"
        #q2 = "match (n:Comment)-[r:RESPONSE_TO]->(m:Comment {comment_id: Q1.COMMENT_ID?) return n"
        #r2 = Relationship(n, "RESPONSE_TO", c)
        #q3 = "match (n:Comment)-[r:RESPONSE_TO]->(m:Comment {comment_id: Q1.COMMENT_ID?) return n"

        
        #full_result = []
        #for r in result:
        #    full_result.append(r)

        #return full_result
        #RETURN C
        """
        """
        PERSON = self.get_player(player_id)
        comments = _relationshoop_matcher.match(person, "CMMENTED ON")
        FOR C IN COMMENTS:
            MORE COMMESNTS = M.END_NODE
    """
    def get_team_comments(self, team_id):
        """
        Gets all of the comments associated with a teams, all of the comments on the comment and comments
        on the comments, etc. Also returns the Nodes for people making the comments.
        :param player_id: ID of the team.
        :return: Graph containing comment, comment streams and commenters.
        """
        q = "MATCH (fan: Fan)-[:RESPONSE_BY]->(coc: Comment)-[:RESPONSE_TO*]->(oc: Comment)-[:COMMENT_ON]->(team:Team {team_id: '" + team_id + "'}), (origin_fan: Fan)-[:COMMENT_BY]->(oc: Comment) RETURN coc, oc, fan, origin_fan"
        #query = self._graph.run(q, player_id)
        #results = query.execute(p=player_id)
        #print(results)
        result = self._graph.run(q).to_table()
        return result.data()
        #print(result)
        #pass













"""
bryankr01   CHN
scherma01   WAS
abreujo02   CHA
ortizda01   BOS
jeterde01   NYA
"""