using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;

public class RandomRoomsCalculator : MonoBehaviour
{
    List<string> vis = new List<string>();
    List<int> rooms = new List<int>();

    List<string> alreadyChosenVis = new List<string>();
    List<int> alreadyChosenRooms = new List<int>();

    List<string> finalValues = new List<string>();
    // Start is called before the first frame update
    void Start()
    {
        rooms.Add(1);
        rooms.Add(2);
        rooms.Add(3);
        rooms.Add(4);
        rooms.Add(5);

        vis.Add("single  ECG  lines");
        vis.Add(" multi  ECG  lines");
        vis.Add("single HEART lines");
        vis.Add(" multi HEART lines");
        vis.Add(" No visualization ");

        Randomize();
    }

    void Randomize()
    {
        int r = -1, v = -1;
        string finalString;

        for(int i = 0; i <= 40; i++)
        {
            alreadyChosenRooms.Clear();
            alreadyChosenVis.Clear();
            for(int j = 1; j <= 5; j++)
            {
                r = Random.Range(0, 5);
                while (alreadyChosenRooms.Contains(rooms[r]))
                {
                    r = Random.Range(0, 5);
                }
                alreadyChosenRooms.Add(rooms[r]);

                v = Random.Range(0, 5);
                while (alreadyChosenVis.Contains(vis[v]))
                {
                    v = Random.Range(0, 5);
                }
                alreadyChosenVis.Add(vis[v]);

            }

            finalString = $"Participant {i}:\nRoom {alreadyChosenRooms[0]}: {alreadyChosenVis[0]}\nRoom {alreadyChosenRooms[1]}: {alreadyChosenVis[1]}\nRoom {alreadyChosenRooms[2]}: {alreadyChosenVis[2]}\nRoom {alreadyChosenRooms[3]}: {alreadyChosenVis[3]}\nRoom {alreadyChosenRooms[4]}: {alreadyChosenVis[4]}\n\n";
            finalValues.Add(finalString);

        }

        File.WriteAllLines("WriteLines.txt", finalValues);
    }
}
