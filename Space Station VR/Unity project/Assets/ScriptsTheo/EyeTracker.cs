using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class EyeTracker : MonoBehaviour
{
    public int participantID;
    public int roomID;
    public string path;
    public string day;

    public GameObject HeadFollow;

    RaycastHit hit;
    Ray ray;

    Dictionary<GameObject, float> objectsTracked = new Dictionary<GameObject, float>();

    List<Vector3> playerPositions = new List<Vector3>();

    float time = 0;
    // Update is called once per frame
    void Update()
    {
        ray = Camera.main.ViewportPointToRay(new Vector3(0.5F, 0.5F, 0));
        
        if (Physics.Raycast(ray, out hit, Mathf.Infinity))
        {
            if(hit.transform.gameObject.tag != "Wall")
            {
                if (objectsTracked.ContainsKey(hit.transform.gameObject))
                {
                    objectsTracked[hit.transform.gameObject] += Time.deltaTime;
                }
                else
                {
                    objectsTracked[hit.transform.gameObject] = Time.deltaTime;
                }
            }
        }


        if(time > 0.1f)
        {
            playerPositions.Add(HeadFollow.transform.position);
            time = 0;
        }

        time += Time.deltaTime;
        
    }

    private void OnApplicationQuit()
    {
        String csv = String.Join(Environment.NewLine, objectsTracked.Select(d => $"{d.Key.ToString().Substring(0, d.Key.ToString().Length - 24)};{(int)d.Value};{" seconds"}"));
        String csv2 = String.Join(Environment.NewLine, playerPositions.Select(d => $"{d.ToString()}"));


        System.IO.File.WriteAllText(path + day + "eye" + participantID + "-" + roomID + ".csv", csv);
        System.IO.File.WriteAllText(path + day + "pos" + participantID + "-" + roomID + ".csv", csv2);
    }
}
